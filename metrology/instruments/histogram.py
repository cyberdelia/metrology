from __future__ import division

import sys

from atomic import AtomicLong, AtomicLongArray

from metrology.stats.sample import UniformSample, ExponentiallyDecayingSample


class Histogram(object):
    """
    A histogram measures the statistical distribution of values in a stream of data. In addition to minimum, maximum, mean, it also measures median, 75th, 90th, 95th, 98th, 99th, and 99.9th percentiles ::

      histogram = Metrology.histogram('response-sizes')
      histogram.update(len(response.content))

    Metrology provides two types of histograms: uniform and exponentially decaying.
    """
    DEFAULT_SAMPLE_SIZE = 1028
    DEFAULT_ALPHA = 0.015

    def __init__(self, sample):
        self.sample = sample
        self.counter = AtomicLong(0)
        self.minimum = AtomicLong(sys.maxsize)
        self.maximum = AtomicLong(-sys.maxsize - 1)
        self.sum = AtomicLong(0)
        self.var = AtomicLongArray([-1, 0])

    def clear(self):
        self.sample.clear()
        self.counter.value = 0
        self.minimum.value = sys.maxsize
        self.maximum.value = (-sys.maxsize - 1)
        self.sum.value = 0
        self.var.value = [-1, 0]

    def update(self, value):
        self.counter += 1
        self.sample.update(value)
        self.max = value
        self.min = value
        self.sum += value
        self.update_variance(value)

    @property
    def snapshot(self):
        return self.sample.snapshot()

    @property
    def count(self):
        """Return number of values."""
        return self.counter.value

    def get_max(self):
        if self.counter.value > 0:
            return self.maximum.value
        return 0.0

    def set_max(self, potential_max):
        done = False
        while not done:
            current_max = self.maximum.value
            done = (current_max is not None and current_max >= potential_max) \
                or self.maximum.compare_and_swap(current_max, potential_max)

    max = property(get_max, set_max, doc="""Returns the maximun value.""")

    def get_min(self):
        if self.counter.value > 0:
            return self.minimum.value
        return 0.0

    def set_min(self, potential_min):
        done = False
        while not done:
            current_min = self.minimum.value
            done = (current_min is not None and current_min <= potential_min) \
                or self.minimum.compare_and_swap(current_min, potential_min)

    min = property(get_min, set_min, doc="""Returns the minimum value.""")

    @property
    def total(self):
        """Returns the total value."""
        return self.sum.value

    @property
    def mean(self):
        """Returns the mean value."""
        if self.counter.value > 0:
            return self.sum.value / self.counter.value
        return 0.0

    @property
    def stddev(self):
        """Returns the standard deviation."""
        if self.counter.value > 0:
            return self.variance ** .5
        return 0.0

    @property
    def variance(self):
        """Returns variance"""
        if self.counter.value <= 1:
            return 0.0
        return self.var.value[1] / (self.counter.value - 1)

    def update_variance(self, value):
        def variance(old_values):
            if old_values[0] == -1:
                new_values = (value, 0)
            else:
                old_m = old_values[0]
                old_s = old_values[1]

                new_m = old_m + ((value - old_m) / self.counter.value)
                new_s = old_s + ((value - old_m) * (value - new_m))

                new_values = (new_m, new_s)
            return new_values
        self.var.value = variance(self.var.value)


class HistogramUniform(Histogram):
    """
    A uniform histogram produces quantiles which are valid for the entirely of the histogram's lifetime. It will return a median value, for example, which is the median of all the values the histogram has ever been updated with.

    Use a uniform histogram when you're interested in long-term measurements. Don't use one where you'd want to know if the distribution of the underlying data stream has changed recently.
    """
    def __init__(self):
        sample = UniformSample(self.DEFAULT_SAMPLE_SIZE)
        super(HistogramUniform, self).__init__(sample)


class HistogramExponentiallyDecaying(Histogram):
    """
    A exponentially decaying histogram produces quantiles which are representative of approximately the last five minutes of data.
    Unlike the uniform histogram, a biased histogram represents recent data, allowing you to know very quickly if the distribution of the data has changed.
    """
    def __init__(self):
        sample = ExponentiallyDecayingSample(self.DEFAULT_SAMPLE_SIZE, self.DEFAULT_ALPHA)
        super(HistogramExponentiallyDecaying, self).__init__(sample)
