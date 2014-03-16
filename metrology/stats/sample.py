import heapq
import math
import random
import sys

from threading import RLock

from atomic import AtomicLong

from metrology.stats.snapshot import Snapshot
from metrology.utils import now


class UniformSample(object):
    def __init__(self, reservoir_size):
        self.counter = AtomicLong(0)
        self.values = [0] * reservoir_size

    def clear(self):
        self.values = [0] * len(self.values)
        self.counter.value = 0

    def size(self):
        count = self.counter.value
        if count > len(self.values):
            return len(self.values)
        return count

    def __len__(self):
        return self.size

    def snapshot(self):
        return Snapshot(self.values[0:self.size()])

    def update(self, value):
        self.counter += 1
        new_count = self.counter.value

        if new_count <= len(self.values):
            self.values[new_count - 1] = value
        else:
            index = random.uniform(0, new_count)
            if index < len(self.values):
                self.values[int(index)] = value


class ExponentiallyDecayingSample(object):
    def __init__(self, reservoir_size, alpha):
        self.values = []
        self.next_scale_time = AtomicLong(0)
        self.alpha = alpha
        self.reservoir_size = reservoir_size
        self.lock = RLock()
        self.rescale_threshold = ExponentiallyDecayingSample.calculate_rescale_threshold(alpha)
        self.clear()

    @staticmethod
    def calculate_rescale_threshold(alpha):
        # determine rescale-threshold such that we will not overflow exp() in
        # weight function, and subsequently not overflow into inf on dividing
        # by random.random()
        min_rand = 1.0 / (2 ** 32)  # minimum non-zero value from random()
        safety = 2.0                # safety pad for numerical inaccuracy
        max_value = sys.float_info.max * min_rand / safety
        return int(math.log(max_value) / alpha)

    def clear(self):
        with self.lock:
            self.values = []
            self.start_time = now()
            self.next_scale_time.value = self.start_time + self.rescale_threshold

    def size(self):
        with self.lock:
            return len(self.values)

    def __len__(self):
        return self.size()

    def snapshot(self):
        with self.lock:
            return Snapshot(val for _, val in self.values)

    def weight(self, timestamp):
        return math.exp(self.alpha * (timestamp - self.start_time))

    def rescale(self, now, next_time):
        if self.next_scale_time.compare_and_swap(next_time, now + self.rescale_threshold):
            with self.lock:
                rescaleFactor = math.exp(-self.alpha * (now - self.start_time))
                self.values = [(k * rescaleFactor, v) for k, v in self.values]
                self.start_time = now

    def rescale_if_necessary(self):
        time = now()
        next_time = self.next_scale_time.value
        if time > next_time:
            self.rescale(time, next_time)

    def update(self, value, timestamp=None):
        if timestamp is None:
            timestamp = now()

        self.rescale_if_necessary()
        with self.lock:
            try:
                priority = self.weight(timestamp) / random.random()
            except (OverflowError, ZeroDivisionError):
                priority = sys.float_info.max

            if len(self.values) < self.reservoir_size:
                heapq.heappush(self.values, (priority, value))
            else:
                heapq.heappushpop(self.values, (priority, value))
