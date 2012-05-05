
from unittest import TestCase

from metrology.instruments.healthcheck import HealthCheck


class DummyHealthCheck(HealthCheck):
    def check(self):
        return True


class HealthCheckTest(TestCase):
    def setUp(self):
        self.health_check = DummyHealthCheck()

    def test_return_check(self):
        self.assertEqual(self.health_check.check(), True)
