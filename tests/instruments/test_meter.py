from threading import Thread
from unittest import TestCase

from metrology.instruments.meter import Meter


class MeterTest(TestCase):
    def setUp(self):
        self.meter = Meter()

    def test_meter(self):
        self.meter.mark()
        self.assertEqual(1, self.meter.count)

    def test_blank_meter(self):
        self.assertEqual(0, self.meter.count)
        self.assertEqual(0.0, self.meter.mean_rate)

    def test_meter_value(self):
        self.meter.mark(3)
        self.assertEqual(3, self.meter.count)

    def test_one_minute_rate(self):
        self.meter.mark(1000)
        self.meter.tick()
        self.assertEqual(200, self.meter.one_minute_rate)

    def test_meter_threaded(self):
        def mark():
            for i in range(100):
                self.meter.mark()
        for thread in [Thread(target=mark) for i in range(10)]:
            thread.start()
            thread.join()
        self.assertEqual(1000, self.meter.count)

    def test_meter_decorator(self):
        @self.meter
        def _test_decorator():
            pass

        for i in range(500):
            _test_decorator()
        self.assertEqual(500, self.meter.count)

    def test_meter_context_manager(self):
        for i in range(275):
            with self.meter:
                pass
        self.assertEqual(275, self.meter.count)

    def tearDown(self):
        self.meter.stop()
