import math

from metrology.exceptions import ArgumentException


class Snapshot(object):
    MEDIAN_Q = 0.5
    P75_Q = 0.75
    P95_Q = 0.95
    P98_Q = 0.98
    P99_Q = 0.99
    P999_Q = 0.999

    def __init__(self, values):
        self.values = sorted(values)

    def value(self, quantile):
        if 0.0 > quantile > 1.0:
            raise ArgumentException("Quantile must be between 0.0 and 1.0")

        if not self.values:
            return 0.0

        pos = quantile * (len(self.values) + 1)

        if pos < 1:
            return self.values[0]

        if pos >= len(self.values):
            return self.values[-1]

        lower = self.values[int(pos) - 1]
        upper = self.values[int(pos)]
        return lower + (pos - math.floor(pos)) * (upper - lower)

    def size(self):
        return len(self.values)

    def __len__(self):
        return self.size()

    @property
    def median(self):
        return self.value(self.MEDIAN_Q)

    @property
    def percentile_75th(self):
        return self.value(self.P75_Q)

    @property
    def percentile_95th(self):
        return self.value(self.P95_Q)

    @property
    def percentile_98th(self):
        return self.value(self.P98_Q)

    @property
    def percentile_99th(self):
        return self.value(self.P99_Q)

    @property
    def percentile_999th(self):
        return self.value(self.P999_Q)
