import time

from metrology.instruments.histogram import HistogramExponentiallyDecaying
from metrology.instruments.meter import Meter


class Timer(object):
    def __init__(self, histogram=HistogramExponentiallyDecaying):
        self.meter = Meter()
        self.histogram = histogram()

    def clear(self):
        self.meter.clear()
        self.histogram.clear()

    def update(self, duration):
        if duration >= 0:
            self.meter.mark()
            self.histogram.update(duration)

    @property
    def snapshot(self):
        return self.histogram.snapshot

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, type, value, callback):
        self.update(time.time() - self.start_time)

    @property
    def count(self):
        return self.histogram.count

    @property
    def one_minute_rate(self):
        return self.meter.one_minute_rate()

    def five_minute_rate(self):
        return self.meter.five_minute_rate()

    def fifteen_minute_rate(self):
        return self.meter.fifteen_minute_rate()

    @property
    def mean_rate(self):
        return self.meter.mean_rate

    @property
    def min(self):
        return self.histogram.min

    @property
    def max(self):
        return self.histogram.max

    @property
    def mean(self):
        return self.histogram.mean

    @property
    def stddev(self):
        return self.histogram.stddev

    def stop(self):
        self.meter.stop()


class UtilizationTimer(Timer):
    def __init__(self):
        super(UtilizationTimer, self).__init__()
        self.duration_meter = Meter()

    def clear(self):
        super(UtilizationTimer, self).clear()
        self.duration_meter.clear()

    def update(self, duration):
        super(UtilizationTimer, self).update(duration)
        if duration >= 0:
            self.duration_meter.mark(duration)

    def one_minute_utilization(self):
        return self.duration_meter.one_minute_rate()

    def five_minute_utilization(self):
        return self.duration_meter.five_minute_rate()

    def fifteen_minute_utilization(self):
        return self.duration_meter.fifteen_minute_rate()

    def mean_utilization(self):
        return self.duration_meter.mean_rate()

    def stop(self):
        super(UtilizationTimer, self).stop()
        self.duration_meter.stop()
