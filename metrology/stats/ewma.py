import math

from atomic import AtomicLong


class EWMA(object):
    INTERVAL = 5.0
    SECONDS_PER_MINUTE = 60.0

    ONE_MINUTE = 1
    FIVE_MINUTES = 5
    FIFTEEN_MINUTES = 15

    M1_ALPHA = 1 - math.exp(-INTERVAL / SECONDS_PER_MINUTE / ONE_MINUTE)
    M5_ALPHA = 1 - math.exp(-INTERVAL / SECONDS_PER_MINUTE / FIVE_MINUTES)
    M15_ALPHA = 1 - math.exp(-INTERVAL / SECONDS_PER_MINUTE / FIFTEEN_MINUTES)

    @classmethod
    def m1(cls):
        return EWMA(cls.M1_ALPHA, cls.INTERVAL)

    @classmethod
    def m5(cls):
        return EWMA(cls.M5_ALPHA, cls.INTERVAL)

    @classmethod
    def m15(cls):
        return EWMA(cls.M15_ALPHA, cls.INTERVAL)

    def __init__(self, alpha, interval):
        self.alpha = alpha
        self.interval = interval

        self.initialized = False
        self._rate = 0.0
        self._uncounted = AtomicLong(0)

    def clear(self):
        self.initialized = False
        self._rate = 0.0
        self._uncounted.value = 0

    def update(self, value):
        self._uncounted += value

    def tick(self):
        count = self._uncounted.swap(0)
        instant_rate = count / self.interval

        if self.initialized:
            self._rate += self.alpha * (instant_rate - self._rate)
        else:
            self._rate = instant_rate
            self.initialized = True

    @property
    def rate(self):
        return self._rate
