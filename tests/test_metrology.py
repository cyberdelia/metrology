from unittest import TestCase

from metrology import Metrology
from metrology.instruments.gauge import Gauge
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
