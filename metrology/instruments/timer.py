from astrolabe.interval import Interval

from metrology.instruments.histogram import HistogramExponentiallyDecaying
from metrology.instruments.meter import Meter


class Timer(object):
    """
    A timer measures both the rate that a particular piece of code is called and the distribution of its duration ::

      timer = Metrology.timer('responses')
      with timer:
          do_something()

    """
    def __init__(self, histogram=HistogramExponentiallyDecaying):
        self.meter = Meter()
        self.histogram = histogram()

    def __call__(self, *args, **kwargs):
        if args and hasattr(args[0], '__call__'):
            _orig_func = args[0]
            def _decorator(*args, **kwargs):
                with self:
                    _orig_func(*args, **kwargs)
            return _decorator

    def clear(self):
        self.meter.clear()
        self.histogram.clear()

    def update(self, duration):
        """Records the duration of an operation."""
        if duration >= 0:
            self.meter.mark()
            self.histogram.update(duration)

    @property
    def snapshot(self):
        return self.histogram.snapshot

    def __enter__(self):
        self.interval = Interval.now()
        return self

    def __exit__(self, type, value, callback):
        duration = self.interval.stop()
        self.update(duration)

    @property
    def total_time(self):
        """Returns the total time spent."""
        return self.histogram.total

    @property
    def count(self):
        """Returns the number of measurements that have been made."""
        return self.histogram.count

    @property
    def one_minute_rate(self):
        """Returns the one-minute average rate."""
        return self.meter.one_minute_rate

    @property
    def five_minute_rate(self):
        """Returns the five-minute average rate."""
        return self.meter.five_minute_rate

    @property
    def fifteen_minute_rate(self):
        """Returns the fifteen-minute average rate."""
        return self.meter.fifteen_minute_rate

    @property
    def mean_rate(self):
        """Returns the mean rate of the events since the start of the process."""
        return self.meter.mean_rate

    @property
    def min(self):
        """Returns the minimum amount of time spent in the operation."""
        return self.histogram.min

    @property
    def max(self):
        """Returns the maximum amount of time spent in the operation."""
        return self.histogram.max

    @property
    def mean(self):
        """Returns the mean time spent in the operation."""
        return self.histogram.mean

    @property
    def stddev(self):
        """Returns the standard deviation of the mean spent in the operation."""
        return self.histogram.stddev

    def stop(self):
        self.meter.stop()


class UtilizationTimer(Timer):
    """
    A specialized timer that calculates the percentage of wall-clock time that was spent ::

      utimer = Metrology.utilization_timer('responses')
      with utimer:
        do_something()

    """
    def __init__(self, histogram=HistogramExponentiallyDecaying):
        super(UtilizationTimer, self).__init__(histogram)
        self.duration_meter = Meter()

    def clear(self):
        super(UtilizationTimer, self).clear()
        self.duration_meter.clear()

    def update(self, duration):
        super(UtilizationTimer, self).update(duration)
        if duration >= 0:
            self.duration_meter.mark(duration)

    @property
    def one_minute_utilization(self):
        """Returns the one-minute average utilization as a percentage."""
        return self.duration_meter.one_minute_rate

    @property
    def five_minute_utilization(self):
        """Returns the five-minute average utilization as a percentage."""
        return self.duration_meter.five_minute_rate

    @property
    def fifteen_minute_utilization(self):
        """Returns the fifteen-minute average utilization as a percentage."""
        return self.duration_meter.fifteen_minute_rate

    @property
    def mean_utilization(self):
        """Returns the mean (average) utilization as a percentage since the process started."""
        return self.duration_meter.mean_rate

    def stop(self):
        super(UtilizationTimer, self).stop()
        self.duration_meter.stop()
