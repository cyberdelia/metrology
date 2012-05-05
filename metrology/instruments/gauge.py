from __future__ import division

import math

from atomic import Atomic


class Gauge(object):
    """
    A gauge is an instantaneous measurement of a value ::

      class JobGauge(metrology.instruments.Gauge):
          def value(self):
              return len(queue)

      gauge = Metrology.gauge('pending-jobs', JobGauge())

    """
    @property
    def value(self):
        """"""
        raise NotImplementedError


class RatioGauge(Gauge):
    """A ratio gauge is a simple way to create a gauge which is the ratio between two numbers"""
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
    """A percent gauge is a ratio gauge where the result is normalized to a value between 0 and 100."""
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
