from unittest import TestCase

from metrology.instruments.derive import Derive


class DeriveTest(TestCase):
    def setUp(self):
        self.derive = Derive()

    def test_derive(self):
        self.derive.mark()
        self.assertEqual(1, self.derive.count)

    def test_blank_derive(self):
        self.assertEqual(0, self.derive.count)
        self.assertEqual(0.0, self.derive.mean_rate)

    def test_derive_value(self):
        self.derive.mark(3)
        self.assertEqual(3, self.derive.count)

    def test_one_minute_rate(self):
        self.derive.mark(1000)
        self.derive.tick()
        self.assertEqual(200, self.derive.one_minute_rate)

    def tearDown(self):
        self.derive.stop()
