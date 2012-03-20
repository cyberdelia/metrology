import time

from atomic import Atomic

from metrology.stats import EWMA
from metrology.utils.periodic import PeriodicTask


class Meter(object):
    def __init__(self, average_class=EWMA):
        self.counter = Atomic(0)
        self.start_time = time.time()

        self.m1_rate = EWMA.m1()
        self.m5_rate = EWMA.m5()
        self.m15_rate = EWMA.m15()

        self.task = PeriodicTask(interval=average_class.INTERVAL,
            target=self.tick)
        self.task.start()

    @property
    def count(self):
        return self.counter.value

    def clear(self):
        self.counter.value = 0
        self.start_time = time.time()

        self.m1_rate.clear()
        self.m5_rate.clear()
        self.m15_rate.clear()

    def mark(self, value=1):
        with self.counter:
            self.counter.value += value
        self.m1_rate.update(value)
        self.m5_rate.update(value)
        self.m15_rate.update(value)

    def tick(self):
        self.m1_rate.tick()
        self.m5_rate.tick()
        self.m15_rate.tick()

    @property
    def one_minute_rate(self):
        return self.m1_rate.rate

    @property
    def five_minute_rate(self):
        return self.m5_rate.rate

    @property
    def fifteen_minute_rate(self):
        return self.m15_rate.rate

    @property
    def mean_rate(self):
        if self.counter.value == 0:
            return 0.0
        else:
            elapsed = time.time() - self.start_time
            return self.counter.value / elapsed

    def stop(self):
        self.task.stop()
