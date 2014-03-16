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
        self.assertAlmostEqual(100, self.timer.mean, delta=10)
        self.assertAlmostEqual(100, self.timer.snapshot.median, delta=10)


class UtilizationTimerTest(TestCase):
    def setUp(self):
        self.timer = UtilizationTimer()

    def tearDown(self):
        self.timer.stop()

    def test_timer(self):
        for i in range(5):
            self.timer.update(100)
            self.timer.update(150)
        self.timer.meter.tick()
        self.timer.duration_meter.tick()

        self.assertAlmostEqual(250, self.timer.one_minute_utilization, delta=10)
