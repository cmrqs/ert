from ert_gui import ERT
from ert_gui.ertwidgets.models.ertmodel import getCurrentCaseName
from ert_gui.models import ErtConnector
from ert_gui.models.mixins import BasicModelMixin


class TargetCaseFormatModel(ErtConnector, BasicModelMixin):
    def __init__(self):
        self.__target_case_fmt = self.getDefaultName()
        self.__custom = False
        ERT.ertChanged.connect(self.__caseChanged)
        super(TargetCaseFormatModel, self).__init__()


    def getValue(self):
        """ @rtype: str """
        return self.__target_case_fmt


    def setValue(self, target_case):
        if target_case is None or target_case.strip() == "" or target_case == self.getDefaultName():
            self.__custom = False
            self.__target_case_fmt = self.getDefaultName()
        else:
            self.__custom = True
            self.__target_case_fmt = target_case

        self.observable().notify(self.VALUE_CHANGED_EVENT)


    def getDefaultName(self):
        """ @rtype: str """
        if self.ert().analysisConfig().getAnalysisIterConfig().caseFormatSet():
            return self.ert().analysisConfig().getAnalysisIterConfig().getCaseFormat()
        else:
            case_name = getCurrentCaseName()
            return "%s_%%d" % case_name


    def __caseChanged(self):
        if not self.__custom:
            self.__target_case_fmt = self.getDefaultName()
            self.observable().notify(self.VALUE_CHANGED_EVENT)