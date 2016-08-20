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

    def test_timer_decorator(self):
        @self.timer
        def _test_decorator():
            time.sleep(0.075)

        for i in range(3):
            _test_decorator()

        self.assertAlmostEqual(75, self.timer.mean, delta=10)
        self.assertAlmostEqual(75, self.timer.snapshot.median, delta=10)

    def test_timer_context_manager(self):
        for i in range(3):
            with self.timer:
                time.sleep(0.035)

        self.assertAlmostEqual(35, self.timer.mean, delta=10)
        self.assertAlmostEqual(35, self.timer.snapshot.median, delta=10)


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
