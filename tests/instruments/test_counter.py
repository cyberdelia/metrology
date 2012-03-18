from unittest import TestCase

from metrology.instruments.counter import Counter


class CounterTest(TestCase):
    def setUp(self):
        self.counter = Counter()

    def test_increment(self):
        self.counter.increment()
        self.assertEqual(1, self.counter.count)

    def test_increment_more(self):
        self.counter.increment(10)
        self.assertEqual(10, self.counter.count)

    def test_clear(self):
        self.counter.increment(10)
        self.counter.clear()
        self.assertEqual(0, self.counter.count)

    def test_decrement(self):
        self.counter.increment(10)
        self.counter.decrement()
        self.assertEqual(9, self.counter.count)

    def test_decrement_more(self):
        self.counter.increment(10)
        self.counter.decrement(9)
        self.assertEqual(1, self.counter.count)
