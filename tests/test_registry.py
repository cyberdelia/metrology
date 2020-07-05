from unittest import TestCase

from metrology.registry import Registry
from metrology.instruments.gauge import Gauge
from metrology.instruments.healthcheck import HealthCheck
from metrology.exceptions import RegistryException


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

    def test_identity(self):
        a = self.registry.counter("test")
        b = self.registry.counter("test")
        self.assertEqual(id(a), id(b))

    def test_separation(self):
        a = self.registry.counter("test")
        b = self.registry.counter("test2")
        self.assertNotEqual(id(a), id(b))

    def test_type_identity(self):
        self.registry.counter("test")
        with self.assertRaises(RegistryException):
            self.registry.histogram("test")

    def test_identity_w_tags(self):
        a = self.registry.counter({
                "name": "test",
                "type": "A"
            })
        b = self.registry.counter({
                "name": "test",
                "type": "A"
            })
        self.assertEqual(id(a), id(b))

    def test_separation_w_tags(self):
        a = self.registry.counter({
                "name": "test",
                "type": "A"
            })
        b = self.registry.counter({
                "name": "test",
                "type": "B"
            })
        self.assertNotEqual(id(a), id(b))

    def test_type_identity_w_tags(self):
        self.registry.counter({
                "name": "test",
                "type": "A"
            })
        with self.assertRaises(RegistryException):
            self.registry.histogram({
                "name": "test",
                "type": "A"
            })
