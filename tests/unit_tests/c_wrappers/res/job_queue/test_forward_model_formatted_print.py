import datetime
import json
import os
import os.path
import stat

import pytest

from ert._c_wrappers.job_queue.environment_varlist import EnvironmentVarlist
from ert._c_wrappers.job_queue.ext_job import ExtJob
from ert._c_wrappers.job_queue.ext_joblist import ExtJoblist
from ert._c_wrappers.job_queue.forward_model import ForwardModel
from ert._c_wrappers.util.substitution_list import SubstitutionList
from ert.simulator.forward_model_status import ForwardModelStatus

joblist = [
    {
        "name": "PERLIN",
        "executable": "perlin.py",
        "target_file": "my_target_file",
        "error_file": "error_file",
        "start_file": "some_start_file",
        "stdout": "perlin.stdout",
        "stderr": "perlin.stderr",
        "stdin": "input4thewin",
        "argList": ["-speed", "hyper"],
        "environment": {"TARGET": "flatland"},
        "license_path": "this/is/my/license/PERLIN",
        "max_running_minutes": 12,
        "max_running": 30,
    },
    {
        "name": "AGGREGATOR",
        "executable": "aggregator.py",
        "target_file": "target",
        "error_file": "None",
        "start_file": "eple",
        "stdout": "aggregator.stdout",
        "stderr": "aggregator.stderr",
        "stdin": "illgiveyousome",
        "argList": ["-o"],
        "environment": {"STATE": "awesome"},
        "license_path": "I/will/pay/ya/tomorrow/AGGREGATOR",
        "max_running_minutes": 1,
        "max_running": 14,
    },
    {
        "name": "PI",
        "executable": "pi.py",
        "target_file": "my_target_file",
        "error_file": "error_file",
        "start_file": "some_start_file",
        "stdout": "pi.stdout",
        "stderr": "pi.stderr",
        "stdin": "input4thewin",
        "argList": ["-p", "8"],
        "environment": {"LOCATION": "earth"},
        "license_path": "license/PI",
        "max_running_minutes": 12,
        "max_running": 30,
    },
    {
        "name": "OPTIMUS",
        "executable": "optimus.py",
        "target_file": "target",
        "error_file": "None",
        "start_file": "eple",
        "stdout": "optimus.stdout",
        "stderr": "optimus.stderr",
        "stdin": "illgiveyousome",
        "argList": ["-help"],
        "environment": {"PATH": "/ubertools/4.1"},
        "license_path": "license/OPTIMUS",
        "max_running_minutes": 1,
        "max_running": 14,
    },
]

#
# Keywords for the ext_job initialization file
#
ext_job_keywords = [
    "MAX_RUNNING",
    "STDIN",
    "STDOUT",
    "STDERR",
    "EXECUTABLE",
    "TARGET_FILE",
    "ERROR_FILE",
    "START_FILE",
    "ARGLIST",
    "ENV",
    "MAX_RUNNING_MINUTES",
]

#
# JSON keywords
#
json_keywords = [
    "name",
    "executable",
    "target_file",
    "error_file",
    "start_file",
    "stdout",
    "stderr",
    "stdin",
    "license_path",
    "max_running_minutes",
    "max_running",
    "argList",
    "environment",
]


def str_none_sensitive(x):
    return str(x) if x is not None else None


DEFAULT_NAME = "default_job_name"


def _generate_job(
    name,
    executable,
    target_file,
    error_file,
    start_file,
    stdout,
    stderr,
    stdin,
    environment,
    arglist,
    max_running_minutes,
    max_running,
    license_root_path,
    private,
):
    config_file = DEFAULT_NAME if name is None else name
    environment = (
        None
        if environment is None
        else list(environment.keys()) + list(environment.values())
    )

    values = [
        str_none_sensitive(max_running),
        stdin,
        stdout,
        stderr,
        executable,
        target_file,
        error_file,
        start_file,
        None if arglist is None else " ".join(arglist),
        None if environment is None else " ".join(environment),
        str_none_sensitive(max_running_minutes),
    ]

    with open(config_file, "w", encoding="utf-8") as conf:
        for key, val in zip(ext_job_keywords, values):
            if val is not None:
                conf.write(f"{key} {val}\n")

    with open(executable, "w", encoding="utf-8"):
        pass
    mode = os.stat(executable).st_mode
    mode |= stat.S_IXUSR | stat.S_IXGRP
    os.chmod(executable, stat.S_IMODE(mode))

    ext_job = ExtJob(config_file, private, name, license_root_path)
    os.unlink(config_file)
    os.unlink(executable)

    return ext_job


def empty_list_if_none(_list):
    return [] if _list is None else _list


def default_name_if_none(name):
    return DEFAULT_NAME if name is None else name


def get_license_root_path(license_path):
    return os.path.split(license_path)[0]


def load_configs(config_file):
    with open(config_file, "r") as cf:
        jobs = json.load(cf)

    return jobs


def create_std_file(config, std="stdout", job_index=None):
    if job_index is None:
        if config[std]:
            return f"{config[std]}"
        else:
            return f'{config["name"]}.{std}'
    else:
        if config[std]:
            return f"{config[std]}.{job_index}"
        else:
            return f'{config["name"]}.{std}.{job_index}'


JOBS_JSON_FILE = "jobs.json"


def validate_ext_job(ext_job, ext_job_config):
    def zero_if_none(x):
        if x is None:
            return 0
        return x

    assert ext_job.name() == default_name_if_none(ext_job_config["name"])
    assert ext_job.get_executable() == ext_job_config["executable"]
    assert ext_job.get_target_file() == ext_job_config["target_file"]
    assert ext_job.get_error_file() == ext_job_config["error_file"]
    assert ext_job.get_start_file() == ext_job_config["start_file"]
    assert ext_job.get_stdout_file() == create_std_file(ext_job_config, std="stdout")
    assert ext_job.get_stderr_file() == create_std_file(ext_job_config, std="stderr")
    assert ext_job.get_stdin_file() == ext_job_config["stdin"]
    assert ext_job.get_max_running_minutes() == zero_if_none(
        ext_job_config["max_running_minutes"]
    )
    assert ext_job.get_max_running() == zero_if_none(ext_job_config["max_running"])
    assert ext_job.get_license_path() == ext_job_config["license_path"]
    assert ext_job.get_arglist() == empty_list_if_none(ext_job_config["argList"])
    if ext_job_config["environment"] is None:
        assert len(ext_job.get_environment().keys()) == 0
    else:
        assert ext_job.get_environment().keys() == ext_job_config["environment"].keys()
        for key in ext_job_config["environment"].keys():
            assert ext_job.get_environment()[key] == ext_job_config["environment"][key]


def generate_job_from_dict(ext_job_config, private=True):
    import copy

    ext_job_config = copy.deepcopy(ext_job_config)
    ext_job_config["executable"] = os.path.join(
        os.getcwd(), ext_job_config["executable"]
    )
    ext_job = _generate_job(
        ext_job_config["name"],
        ext_job_config["executable"],
        ext_job_config["target_file"],
        ext_job_config["error_file"],
        ext_job_config["start_file"],
        ext_job_config["stdout"],
        ext_job_config["stderr"],
        ext_job_config["stdin"],
        ext_job_config["environment"],
        ext_job_config["argList"],
        ext_job_config["max_running_minutes"],
        ext_job_config["max_running"],
        get_license_root_path(ext_job_config["license_path"]),
        private,
    )

    validate_ext_job(ext_job, ext_job_config)
    return ext_job


def set_up_forward_model(selected_jobs=None):
    if selected_jobs is None:
        selected_jobs = range(len(joblist))
    jobs = [generate_job_from_dict(job) for job in joblist]

    ext_joblist = ExtJoblist()
    for job in jobs:
        ext_joblist.add_job(job.name(), job)

    forward_model = ForwardModel(ext_joblist)
    for index in selected_jobs:
        forward_model.add_job(jobs[index].name())

    return forward_model


def verify_json_dump(selected_jobs, global_args, run_id):
    assert os.path.isfile(JOBS_JSON_FILE)
    config = load_configs(JOBS_JSON_FILE)

    assert run_id == config["run_id"]
    assert len(selected_jobs) == len(config["jobList"])

    for job_index, selected_job in enumerate(selected_jobs):
        job = joblist[selected_job]
        loaded_job = config["jobList"][job_index]

        # Since no argList is loaded as an empty list by ext_job
        arg_list_back_up = job["argList"]
        job["argList"] = empty_list_if_none(job["argList"])

        # Since name is set to default if none provided by ext_job
        name_back_up = job["name"]
        job["name"] = default_name_if_none(job["name"])

        for key in json_keywords:
            if key in ["stdout", "stderr"]:
                assert (
                    create_std_file(job, std=key, job_index=job_index)
                    == loaded_job[key]
                )
            elif key == "executable":
                assert job[key] in loaded_job[key]
            else:
                assert job[key] == loaded_job[key]

        job["argList"] = arg_list_back_up
        job["name"] = name_back_up


@pytest.mark.usefixtures("use_tmpdir")
def test_no_jobs():
    forward_model = set_up_forward_model([])
    run_id = "test_no_jobs_id"
    global_args = SubstitutionList()
    varlist = EnvironmentVarlist()
    forward_model.formatted_fprintf(
        run_id, os.getcwd(), "data_root", global_args, varlist
    )

    verify_json_dump([], global_args, run_id)


@pytest.mark.usefixtures("use_tmpdir")
def test_transfer_arg_types():
    with open("FWD_MODEL", "w") as f:
        f.write("EXECUTABLE ls\n")
        f.write("MIN_ARG 2\n")
        f.write("MAX_ARG 6\n")
        f.write("ARG_TYPE 0 INT\n")
        f.write("ARG_TYPE 1 FLOAT\n")
        f.write("ARG_TYPE 2 STRING\n")
        f.write("ARG_TYPE 3 BOOL\n")
        f.write("ARG_TYPE 4 RUNTIME_FILE\n")
        f.write("ARG_TYPE 5 RUNTIME_INT\n")
        f.write("ENV KEY1 VALUE2\n")
        f.write("ENV KEY2 VALUE2\n")

    job = ExtJob("FWD_MODEL", True)

    ext_joblist = ExtJoblist()
    ext_joblist.add_job(job.name(), job)
    forward_model = ForwardModel(ext_joblist)
    forward_model.add_job("FWD_MODEL")

    run_id = "test_no_jobs_id"
    global_args = SubstitutionList()

    forward_model.formatted_fprintf(
        run_id,
        os.getcwd(),
        "data_root",
        global_args,
        EnvironmentVarlist(),
    )
    config = load_configs(JOBS_JSON_FILE)
    printed_job = config["jobList"][0]
    assert printed_job["min_arg"] == 2
    assert printed_job["max_arg"] == 6
    assert printed_job["arg_types"] == [
        "INT",
        "FLOAT",
        "STRING",
        "BOOL",
        "RUNTIME_FILE",
        "RUNTIME_INT",
    ]


@pytest.mark.usefixtures("use_tmpdir")
def test_env_varlist():
    varlist_string = "global_environment"
    update_string = "global_update_path"
    first = "FIRST"
    second = "SECOND"
    third = "THIRD"
    first_value = "TheFirstValue"
    second_value = "TheSecondValue"
    third_value = "$FIRST:$SECOND"
    third_value_correct = f"{first_value}:{second_value}"
    varlist = EnvironmentVarlist(
        {first: first_value, second: second_value, third: third_value}
    )
    forward_model = set_up_forward_model([])
    run_id = "test_no_jobs_id"
    global_args = SubstitutionList()
    forward_model.formatted_fprintf(
        run_id, os.getcwd(), "data_root", global_args, varlist
    )
    config = load_configs(JOBS_JSON_FILE)
    env_config = config[varlist_string]
    assert first_value == env_config[first]
    assert second_value == env_config[second]
    assert third_value_correct == env_config[third]
    # pylint: disable=pointless-statement
    config[update_string]


@pytest.mark.usefixtures("use_tmpdir")
def test_repr():
    forward_model = set_up_forward_model()
    assert repr(forward_model).startswith("ForwardModel")


@pytest.mark.usefixtures("use_tmpdir")
def test_one_job():
    for i in range(len(joblist)):
        forward_model = set_up_forward_model([i])
        run_id = "test_one_job"
        global_args = SubstitutionList()
        varlist = EnvironmentVarlist()
        forward_model.formatted_fprintf(
            run_id, os.getcwd(), "data_root", global_args, varlist
        )

        verify_json_dump([i], global_args, run_id)


def run_all():
    forward_model = set_up_forward_model(range(len(joblist)))
    run_id = "run_all"
    global_args = SubstitutionList()
    varlist = EnvironmentVarlist()
    forward_model.formatted_fprintf(
        run_id, os.getcwd(), "data_root", global_args, varlist
    )

    verify_json_dump(range(len(joblist)), global_args, run_id)


@pytest.mark.usefixtures("use_tmpdir")
def test_all_jobs():
    run_all()


@pytest.mark.usefixtures("use_tmpdir")
def test_name_none():
    name_back_up = joblist[0]["name"]
    license_path_back_up = joblist[0]["license_path"]

    joblist[0]["name"] = None
    joblist[0]["license_path"] = os.path.join(
        get_license_root_path(joblist[0]["license_path"]), DEFAULT_NAME
    )

    run_all()

    joblist[0]["name"] = name_back_up
    joblist[0]["license_path"] = license_path_back_up


@pytest.mark.usefixtures("use_tmpdir")
def test_various_null_fields():
    for key in [
        "target_file",
        "error_file",
        "start_file",
        "stdout",
        "stderr",
        "max_running_minutes",
        "argList",
        "environment",
        "stdin",
    ]:
        back_up = joblist[0][key]
        joblist[0][key] = None
        run_all()
        joblist[0][key] = back_up


@pytest.mark.usefixtures("use_tmpdir")
def test_status_file():
    forward_model = set_up_forward_model()
    run_id = "test_no_jobs_id"
    global_args = SubstitutionList()
    varlist = EnvironmentVarlist()
    forward_model.formatted_fprintf(
        run_id, os.getcwd(), "data_root", global_args, varlist
    )

    s = (
        '{"start_time": null, "jobs": [{"status": "Success", '
        '"start_time": 1519653419.0, "end_time": 1519653419.0, '
        '"name": "SQUARE_PARAMS", "error": null, "current_memory_usage": 2000, '
        '"max_memory_usage": 3000}], "end_time": null, "run_id": ""}'
    )

    with open("status.json", "w") as f:
        f.write(s)

    status = ForwardModelStatus.try_load("")
    for job in status.jobs:
        assert isinstance(job.start_time, datetime.datetime)
        assert isinstance(job.end_time, datetime.datetime)