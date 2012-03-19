import time

from unittest import TestCase

from metrology.instruments.timer import Timer, UtilizationTimer


class TimerTest(TestCase):
    def setUp(self):
        self.timer = Timer()

    def tearDown(self):
        self.timer.stop()

    def test_timer(self):
        for i in range(3):
            with self.timer:
                time.sleep(0.1)
        self.assertAlmostEqual(0.1, self.timer.mean, 1)
        self.assertAlmostEqual(0.1, self.timer.snapshot.median, 1)


class UtilizationTimerTest(TestCase):
    def setUp(self):
        self.timer = UtilizationTimer()

    def tearDown(self):
        self.timer.stop()

    def test_timer(self):
        for i in range(5):
            self.timer.update(0.10)
            self.timer.update(0.15)
        self.timer.meter.tick()
        self.timer.duration_meter.tick()

        self.assertAlmostEqual(0.25, self.timer.one_minute_utilization, 1)
