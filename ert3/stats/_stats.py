import numpy as np
import scipy.stats


class Distribution:
    def __init__(self, *, size, index, rvs, ppf):
        if size is None and index is None:
            raise ValueError(
                "Cannot create distribution with neither size nor index"
            )
        if size is not None and index is not None:
            raise ValueError(
                "Cannot create distribution with both size and index"
            )

        if size is not None:
            self._size = size
            self._as_array = True
            self._index = tuple(range(self._size))
        else:
            self._size = len(tuple(index))
            self._as_array = False
            self._index = tuple(index)

        self._raw_rvs = rvs
        self._raw_ppf = ppf

    @property
    def index(self):
        return self._index

    def _add_index(self, x):
        if self._as_array:
            return x 
        else:
            return {idx: float(val) for idx, val in zip(self.index, x)}

    def sample(self):
        return self._add_index(self._raw_rvs(self._size))

    def ppf(self, x):
        x = np.full(self._size, x)
        result = self._raw_ppf(x)
        return self._add_index(result)


class Gaussian(Distribution):
    def __init__(self, mean, std, *, size=None, index=None):
        self._mean = mean
        self._std = std

        rvs = lambda size: scipy.stats.norm.rvs(
            loc=self._mean, scale=self._std, size=size
        )
        ppf = lambda x: scipy.stats.norm.ppf(
            x, loc=self._mean, scale=self._std
        )

        super().__init__(
            size=size,
            index=index,
            rvs=rvs,
            ppf=ppf,
        )


class Uniform(Distribution):
    def __init__(self, lower_bound, upper_bound, *, size=None, index=None):
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound
        self._scale = upper_bound - lower_bound

        rvs = lambda size: scipy.stats.uniform.rvs(
            loc=self._lower_bound, scale=self._scale, size=self._size
        )
        ppf = lambda x: scipy.stats.uniform.ppf(
            x, loc=self._lower_bound, scale=self._scale
        )

        super().__init__(
            size=size,
            index=index,
            rvs=rvs,
            ppf=ppf,
        )
