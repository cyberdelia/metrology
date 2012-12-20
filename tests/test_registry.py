from unittest import TestCase

from metrology.registry import Registry
from metrology.instruments.gauge import Gauge
from metrology.instruments.healthcheck import HealthCheck


class DummyGauge(Gauge):
    def value(self):
        return "wow"


class DummyHealthCheck(HealthCheck):
    def check(self):
        return True


class RegistryTest(TestCase):
    def setUp(self):
        self.registry = Registry()

    def tearDown(self):
        self.registry.stop()

    def test_counter(self):
        self.assertTrue(self.registry.counter('test') is not None)

    def test_meter(self):
        self.assertTrue(self.registry.meter('test') is not None)

    def test_gauge(self):
        self.assertTrue(self.registry.gauge('test', DummyGauge()) is not None)

    def test_timer(self):
        self.assertTrue(self.registry.timer('test') is not None)

    def test_utilization_timer(self):
        self.assertTrue(self.registry.utilization_timer('test') is not None)

    def test_histogram(self):
        self.assertTrue(self.registry.histogram('test') is not None)

    def test_health_check(self):
        health = self.registry.health_check('test', DummyHealthCheck())
        self.assertTrue(health is not None)
