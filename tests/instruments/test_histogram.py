from threading import Thread
from unittest import TestCase

from metrology.instruments.histogram import HistogramUniform, HistogramExponentiallyDecaying


class HistogramTest(TestCase):
    def test_uniform_sample_min(self):
        histogram = HistogramUniform()
        histogram.update(5)
        histogram.update(10)
        self.assertEqual(5, histogram.min)

    def test_uniform_sample_max(self):
        histogram = HistogramUniform()
        histogram.update(5)
        histogram.update(10)
        self.assertEqual(10, histogram.max)

    def test_uniform_sample_mean(self):
        histogram = HistogramUniform()
        histogram.update(5)
        histogram.update(10)
        self.assertEqual(7.5, histogram.mean)

    def test_uniform_sample_mean_threaded(self):
        histogram = HistogramUniform()

        def update():
            for i in range(100):
                histogram.update(5)
                histogram.update(10)
        for thread in [Thread(target=update) for i in range(10)]:
            thread.start()
            thread.join()
        self.assertEqual(7.5, histogram.mean)

    def test_uniform_sample_2000(self):
        histogram = HistogramUniform()
        for i in range(2000):
            histogram.update(i)
        self.assertEqual(1999, histogram.max)

    def test_uniform_sample_snapshot(self):
        histogram = HistogramUniform()
        for i in range(100):
            histogram.update(i)
        snapshot = histogram.snapshot
        self.assertEqual(49.5, snapshot.median)

    def test_uniform_sample_snapshot_threaded(self):
        histogram = HistogramUniform()

        def update():
            for i in range(100):
                histogram.update(i)
        for thread in [Thread(target=update) for i in range(10)]:
            thread.start()
            thread.join()
        snapshot = histogram.snapshot
        self.assertEqual(49.5, snapshot.median)

    def test_exponential_sample_min(self):
        histogram = HistogramExponentiallyDecaying()
        histogram.update(5)
        histogram.update(10)
        self.assertEqual(5, histogram.min)

    def test_exponential_sample_max(self):
        histogram = HistogramExponentiallyDecaying()
        histogram.update(5)
        histogram.update(10)
        self.assertEqual(10, histogram.max)

    def test_exponential_sample_mean(self):
        histogram = HistogramExponentiallyDecaying()
        histogram.update(5)
        histogram.update(10)
        self.assertEqual(7.5, histogram.mean)

    def test_exponential_sample_mean_threaded(self):
        histogram = HistogramExponentiallyDecaying()

        def update():
            for i in range(100):
                histogram.update(5)
                histogram.update(10)
        for thread in [Thread(target=update) for i in range(10)]:
            thread.start()
            thread.join()
        self.assertEqual(7.5, histogram.mean)

    def test_exponential_sample_2000(self):
        histogram = HistogramExponentiallyDecaying()
        for i in range(2000):
            histogram.update(i)
        self.assertEqual(1999, histogram.max)

    def test_exponential_sample_snapshot(self):
        histogram = HistogramExponentiallyDecaying()
        for i in range(100):
            histogram.update(i)
        snapshot = histogram.snapshot
        self.assertEqual(49.5, snapshot.median)

    def test_exponential_sample_snapshot_threaded(self):
        histogram = HistogramExponentiallyDecaying()

        def update():
            for i in range(100):
                histogram.update(i)
        for thread in [Thread(target=update) for i in range(10)]:
            thread.start()
            thread.join()
        snapshot = histogram.snapshot
        self.assertEqual(49.5, snapshot.median)
