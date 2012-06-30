from __future__ import division

import statprof

from os.path import basename
from collections import defaultdict

from metrology.instruments.histogram import HistogramExponentiallyDecaying


__all__ = ['Profiler']


class _Trace(object):
    def __init__(self, data):
        self_sample_count = data.self_sample_count
        cum_sample_count = data.cum_sample_count
        sample_count = statprof.state.sample_count
        secs_per_sample = statprof.state.accumulated_time / sample_count
        self.name = "{0}.{1}.{2}".format(basename(data.key.filename),
            data.key.name, data.key.lineno)
        self.percent = self_sample_count / sample_count * 100
        self.cumulative = cum_sample_count * secs_per_sample
        self.self = self_sample_count * secs_per_sample


class Profiler(object):
    """
    A profiler measures the distribution of the duration passed in a every part of the code ::

        profiler = Metrology.profiler('slow-code')
        with profiler:
            run_slow_code()

    .. warning::
        This instrument does not yet work on Windows, and it doesn't run on Python 3

    """
    def __init__(self, frequency=None, histogram=HistogramExponentiallyDecaying):
        self.frequency = frequency
        self.traces = defaultdict(histogram)

    def clear(self):
        self.histogram.clear()

    def __enter__(self):
        try:
            statprof.reset(self.frequency)
        except AssertionError:
            pass  # statprof is already running
        statprof.start()
        return self

    def update(self, key, duration):
        """Records the duration of a call."""
        if duration >= 0:
            self.traces[key].update(duration)

    def __exit__(self, type, value, callback):
        statprof.stop()
        for call in statprof.CallData.all_calls.itervalues():
            trace = _Trace(call)
            for attr in ('percent', 'cumulative', 'self'):
                self.update("{0}.{1}".format(trace.name, attr), getattr(trace, attr))

    def stop(self):
        pass
