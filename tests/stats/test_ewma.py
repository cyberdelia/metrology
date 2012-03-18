from unittest import TestCase

from metrology.stats.ewma import EWMA


class EwmaTest(TestCase):
    def _one_minute(self, ewma):
        for i in range(12):
            ewma.tick()

    def test_one_minute_ewma(self):
        ewma = EWMA.m1()
        ewma.update(3)
        ewma.tick()
        self.assertAlmostEqual(ewma.rate, 0.6, places=6)

        self._one_minute(ewma)
        self.assertAlmostEqual(ewma.rate, 0.22072766, places=6)

        self._one_minute(ewma)
        self.assertAlmostEqual(ewma.rate, 0.08120117, places=6)

    def test_five_minute_ewma(self):
        ewma = EWMA.m5()
        ewma.update(3)
        ewma.tick()
        self.assertAlmostEqual(ewma.rate, 0.6, places=6)

        self._one_minute(ewma)
        self.assertAlmostEqual(ewma.rate, 0.49123845, places=6)

        self._one_minute(ewma)
        self.assertAlmostEqual(ewma.rate, 0.40219203, places=6)

    def test_fifteen_minute_ewma(self):
        ewma = EWMA.m15()
        ewma.update(3)
        ewma.tick()
        self.assertAlmostEqual(ewma.rate, 0.6, places=6)

        self._one_minute(ewma)
        self.assertAlmostEqual(ewma.rate, 0.56130419, places=6)

        self._one_minute(ewma)
        self.assertAlmostEqual(ewma.rate, 0.52510399, places=6)

    def test_clear_ewma(self):
        ewma = EWMA.m15()
        ewma.update(3)
        ewma.tick()
        ewma.clear()
        self.assertAlmostEqual(ewma.rate, 0)
