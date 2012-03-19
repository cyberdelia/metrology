from __future__ import division

import math

from atomic import Atomic


class Gauge(object):
    @property
    def value(self):
        raise NotImplementedError


class RatioGauge(Gauge):
    def numerator(self):
        raise NotImplementedError

    def denominator(self):
        raise NotImplementedError

    @property
    def value(self):
        d = self.denominator()
        if math.isnan(d) or math.isinf(d) or d == 0.0 or d == 0:
            return float('nan')
        return self.numerator() / d


class PercentGauge(RatioGauge):
    @property
    def value(self):
        value = super(PercentGauge, self).value
        return value * 100


class ToggleGauge(Gauge):
    _value = Atomic(1)

    @property
    def value(self):
        try:
            return self._value.get()
        finally:
            self._value.set(0)
