from unittest import TestCase

from metrology.stats.sample import UniformSample, ExponentiallyDecayingSample


class UniformSampleTest(TestCase):
    def test_sample(self):
        sample = UniformSample(100)
        for i in range(1000):
            sample.update(i)
        snapshot = sample.snapshot()
        self.assertEqual(sample.size(), 100)
        self.assertEqual(snapshot.size(), 100)

        for value in snapshot.values:
            self.assertTrue(value < 1000.0)
            self.assertTrue(value >= 0.0)


class ExponentiallyDecayingSampleTest(TestCase):
    def test_sample_1000(self):
        sample = ExponentiallyDecayingSample(100, 0.99)
        for i in range(1000):
            sample.update(i)
        self.assertEqual(sample.size(), 100)
        snapshot = sample.snapshot()
        self.assertEqual(snapshot.size(), 100)

        for value in snapshot.values:
            self.assertTrue(value < 1000.0)
            self.assertTrue(value >= 0.0)

    def test_sample_10(self):
        sample = ExponentiallyDecayingSample(100, 0.99)
        for i in range(10):
            sample.update(i)
        self.assertEqual(sample.size(), 10)

        snapshot = sample.snapshot()
        self.assertEqual(snapshot.size(), 10)

        for value in snapshot.values:
            self.assertTrue(value < 10.0)
            self.assertTrue(value >= 0.0)

    def test_sample_100(self):
        sample = ExponentiallyDecayingSample(1000, 0.01)
        for i in range(100):
            sample.update(i)
        self.assertEqual(sample.size(), 100)

        snapshot = sample.snapshot()
        self.assertEqual(snapshot.size(), 100)

        for value in snapshot.values:
            self.assertTrue(value < 100.0)
            self.assertTrue(value >= 0.0)
