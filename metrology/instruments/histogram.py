from __future__ import division

from atomic import Atomic

from metrology.stats.sample import UniformSample, ExponentiallyDecayingSample


class Histogram(object):
    DEFAULT_SAMPLE_SIZE = 1028
    DEFAULT_ALPHA = 0.015

    def __init__(self, sample):
        self.sample = sample
        self.counter = Atomic(0)
        self.minimum = Atomic()
        self.maximum = Atomic()
        self.sum = Atomic(0)
        self.var = Atomic([-1, 0])

    def clear(self):
        self.sample.clear()
        self.counter.value = 0
        self.minimum.value = None
        self.maximum.value = None
        self.sum.value = 0
        self.var.value = [-1, 0]

    def update(self, value):
        with self.counter:
            self.counter.value += 1
        self.sample.update(value)
        self.max = value
        self.min = value
        with self.sum:
            self.sum.value += value
        self.update_variance(value)

    @property
    def snapshot(self):
        return self.sample.snapshot()

    @property
    def count(self):
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

    max = property(get_max, set_max)

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

    min = property(get_min, set_min)

    @property
    def mean(self):
        if self.counter.value > 0:
            return self.sum.value / self.counter.value
        return 0.0

    @property
    def stddev(self):
        if self.counter.value > 0:
            return self.var.value
        return 0.0

    @property
    def variance(self):
        if self.counter.value <= 1:
            return 0.0
        return self.var.value[1] / (self.counter.value - 1)

    def update_variance(self, value):
        with self.var:
            old_values = self.var.value
            if old_values[0] == -1:
                new_values = (value, 0)
            else:
                old_m = old_values[0]
                old_s = old_values[1]

                new_m = old_m + ((value - old_m) / self.counter.value)
                new_s = old_s + ((value - old_m) * (value - new_m))

                new_values = (new_m, new_s)

            self.var.value = new_values
            return new_values


class HistogramUniform(Histogram):
    def __init__(self):
        sample = UniformSample(self.DEFAULT_SAMPLE_SIZE)
        super(HistogramUniform, self).__init__(sample)


class HistogramExponentiallyDecaying(Histogram):
    def __init__(self):
        sample = ExponentiallyDecayingSample(self.DEFAULT_SAMPLE_SIZE, self.DEFAULT_ALPHA)
        super(HistogramExponentiallyDecaying, self).__init__(sample)
