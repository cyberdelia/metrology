import math
import random
import sys

from time import time

from atomic import Atomic
from bintrees.rbtree import RBTree
from threading import RLock

from metrology.stats.snapshot import Snapshot


class UniformSample(object):
    def __init__(self, reservoir_size):
        self.counter = Atomic(0)
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
        new_count = self.counter.update(lambda v: v + 1)

        if new_count <= len(self.values):
            self.values[new_count - 1] = value
        else:
            index = random.uniform(0, new_count)
            if index < len(self.values):
                self.values[int(index)] = value


class ExponentiallyDecayingSample(object):
    RESCALE_THRESHOLD = 60 * 60

    def __init__(self, reservoir_size, alpha):
        self.values = RBTree()
        self.counter = Atomic(0)
        self.next_scale_time = Atomic(0)
        self.alpha = alpha
        self.reservoir_size = reservoir_size
        self.lock = RLock()
        self.clear()

    def clear(self):
        with self.lock:
            self.values.clear()
            self.counter.value = 0
            self.next_scale_time.value = time() + self.RESCALE_THRESHOLD
            self.start_time = time()

    def size(self):
        count = self.counter.value
        if count < self.reservoir_size:
            return count
        return self.reservoir_size

    def __len__(self):
        return self.size()

    def snapshot(self):
        with self.lock:
            return Snapshot(list(self.values.values()))

    def weight(self, timestamp):
        return math.exp(self.alpha * timestamp)

    def rescale(self, now, next_time):
        if self.next_scale_time.compare_and_swap(next_time, now + self.RESCALE_THRESHOLD):
            with self.lock:
                old_start_time = self.start_time
                self.start_time = time()
                for key in list(self.values.keys()):
                    value = self.values.remove(key)
                self.values[key * math.exp(-self.alpha * (self.start_time - old_start_time))] = value

    def update(self, value, timestamp=None):
        if not timestamp:
            timestamp = time()
        with self.lock:
            try:
                priority = self.weight(timestamp - self.start_time) / random.random()
            except OverflowError:
                priority = sys.float_info.max
            new_count = self.counter.update(lambda v: v + 1)

            if math.isnan(priority):
                return

            if new_count <= self.reservoir_size:
                self.values[priority] = value
            else:
                first_priority = self.values.root.key
                if first_priority < priority:
                    if priority in self.values:
                        self.values[priority] = value
                        if not self.values.remove(first_priority):
                            first_priority = self.values.root()
