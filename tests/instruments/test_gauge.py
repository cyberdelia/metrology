import math

from unittest import TestCase

from metrology.instruments.gauge import Gauge, RatioGauge, PercentGauge, \
    ToggleGauge


class DummyGauge(Gauge):
    @property
    def value(self):
        return "wow"


class DummyRatioGauge(RatioGauge):
    def __init__(self, numerator, denominator):
        self.num = numerator
        self.den = denominator

    def numerator(self):
        return self.num

    def denominator(self):
        return self.den


class DummyPercentGauge(DummyRatioGauge, PercentGauge):
    pass


class GaugeTest(TestCase):
    def setUp(self):
        self.gauge = DummyGauge()

    def test_return_value(self):
        self.assertEqual(self.gauge.value, "wow")


class RatioGaugeTest(TestCase):
    def test_ratio(self):
        gauge = DummyRatioGauge(2, 4)
        self.assertEqual(gauge.value, 0.5)

    def test_divide_by_zero(self):
        gauge = DummyRatioGauge(100, 0)
        self.assertTrue(math.isnan(gauge.value))

    def test_divide_by_infinite(self):
        gauge = DummyRatioGauge(100, float('inf'))
        self.assertTrue(math.isnan(gauge.value))

    def test_divide_by_nan(self):
        gauge = DummyRatioGauge(100, float('nan'))
        self.assertTrue(math.isnan(gauge.value))


class PercentGaugeTest(TestCase):
    def test_percentage(self):
        gauge = DummyPercentGauge(2, 4)
        self.assertEqual(gauge.value, 50.)

    def test_with_nan(self):
        gauge = DummyPercentGauge(2, 0)
        self.assertTrue(math.isnan(gauge.value))


class ToggleGaugeTest(TestCase):
    def test_return_one_then_zero(self):
        gauge = ToggleGauge()
        self.assertEqual(gauge.value, 1)
        self.assertEqual(gauge.value, 0)
        self.assertEqual(gauge.value, 0)
        self.assertEqual(gauge.value, 0)
