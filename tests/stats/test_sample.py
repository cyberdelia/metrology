import math

from unittest import TestCase

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch  # noqa

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

    def timestamp_to_priority_is_noop(f):
        """
        Decorator that patches ExponentiallyDecayingSample class such that the
        timestamp->priority function is a no-op.
        """
        weight_fn = "metrology.stats.sample.ExponentiallyDecayingSample.weight"
        return patch(weight_fn, lambda self, x: x)(patch("random.random",
                                                         lambda: 1.0)(f))

    @timestamp_to_priority_is_noop
    def test_sample_eviction(self):
        kSampleSize = 10
        kDefaultValue = 1.0
        sample = ExponentiallyDecayingSample(kSampleSize, 0.01)

        timestamps = range(1, kSampleSize * 2)
        for count, timestamp in enumerate(timestamps):
            sample.update(kDefaultValue, timestamp)
            self.assertLessEqual(len(sample.values), kSampleSize)
            self.assertLessEqual(len(sample.values), count + 1)
            expected_min_key = timestamps[max(0, count + 1 - kSampleSize)]
            self.assertEqual(min(sample.values)[0], expected_min_key)

    @timestamp_to_priority_is_noop
    def test_sample_ordering(self):
        kSampleSize = 3
        sample = ExponentiallyDecayingSample(kSampleSize, 0.01)

        timestamps = range(1, kSampleSize + 1)
        values = ["value_{0}".format(i) for i in timestamps]
        expected = list(zip(timestamps, values))
        for timestamp, value in expected:
            sample.update(value, timestamp)
        self.assertListEqual(sorted(sample.values), expected)

        # timestamp less than any existing => no-op
        sample.update("ignore", 0.5)
        self.assertEqual(sorted(sample.values), expected)

        # out of order insertions
        expected = [3.0, 4.0, 5.0]
        sample.update("ignore", 5.0)
        sample.update("ignore", 4.0)
        self.assertListEqual(sorted(k for k, _ in sample.values), expected)

        # collision
        marker = "marker"
        replacement_timestamp = 5.0
        expected = [4.0, 5.0, 5.0]
        sample.update(marker, replacement_timestamp)
        self.assertListEqual(sorted(k for k, _ in sample.values), expected)

        replacement_timestamp = 4.0
        expected = [4.0, 5.0, 5.0]
        sample.update(marker, replacement_timestamp)
        self.assertListEqual(sorted(k for k, _ in sample.values), expected)

    def test_rescale_threshold(self):
        infinity = float('inf')
        for alpha in (0.015, 1e-10, 1):
            rescale_threshold = \
                ExponentiallyDecayingSample.calculate_rescale_threshold(alpha)
            min_rand_val = 1.0 / (2 ** 32)
            max_priority = math.exp(alpha * rescale_threshold) / min_rand_val
            self.assertLess(max_priority, infinity)
