import test.pystone

from unittest import TestCase

from metrology.instruments.profiler import Profiler


class ProfilerTest(TestCase):
    def setUp(self):
        self.profiler = Profiler()

    def tearDown(self):
        self.profiler.stop()

    def test_profiler(self):
        with self.profiler:
            test.pystone.pystones()
