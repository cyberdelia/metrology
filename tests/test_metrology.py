from unittest import TestCase

from metrology import Metrology
from metrology.instruments.gauge import Gauge
from metrology.instruments.healthcheck import HealthCheck
from metrology.registry import registry


class MetrologyTest(TestCase):
    def setUp(self):
        registry.clear()

    def tearDown(self):
        registry.clear()

    def test_get(self):
        Metrology.counter('test')
        self.assertTrue(Metrology.get('test') is not None)

    def test_counter(self):
        self.assertTrue(Metrology.counter('test') is not None)

    def test_meter(self):
        self.assertTrue(Metrology.meter('test') is not None)

    def test_gauge(self):
        self.assertTrue(Metrology.gauge('test', Gauge) is not None)

    def test_timer(self):
        self.assertTrue(Metrology.timer('test') is not None)

    def test_utilization_timer(self):
        self.assertTrue(Metrology.utilization_timer('test') is not None)

    def test_histogram(self):
        self.assertTrue(Metrology.histogram('test') is not None)

    def test_health_check(self):
        health = Metrology.health_check('test', HealthCheck)
        self.assertTrue(health is not None)
