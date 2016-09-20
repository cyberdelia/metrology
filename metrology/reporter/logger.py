import logging

from metrology.instruments import *  # noqa
from metrology.reporter.base import Reporter


class LoggerReporter(Reporter):
    """
    A logging reporter that write metrics to a logger ::

      reporter = LoggerReporter(level=logging.DEBUG, interval=10)
      reporter.start()

    :param logger: logger to use
    :param level: logger level
    :param interval: time between each reporting
    :param prefix: metrics name prefix
    """
    def __init__(self, logger=logging, level=logging.INFO, **options):
        self.logger = logger
        self.level = level

        self.prefix = options.get('prefix')
        super(LoggerReporter, self).__init__(**options)

    def write(self):
        for name, metric in self.registry:
            if isinstance(metric, Meter):
                self.log_metric(name, 'meter', metric, [
                    'count', 'one_minute_rate', 'five_minute_rate',
                    'fifteen_minute_rate', 'mean_rate'
                ])
            if isinstance(metric, Gauge):
                self.log_metric(name, 'gauge', metric, [
                    'value'
                ])
            if isinstance(metric, UtilizationTimer):
                self.log_metric(name, 'timer', metric, [
                    'count', 'one_minute_rate', 'five_minute_rate',
                    'fifteen_minute_rate', 'mean_rate',
                    'min', 'max', 'mean', 'stddev',
                    'one_minute_utilization', 'five_minute_utilization',
                    'fifteen_minute_utilization', 'mean_utilization'
                ], [
                    'median', 'percentile_95th'
                ])
            if isinstance(metric, Timer):
                self.log_metric(name, 'timer', metric, [
                    'count', 'total_time', 'one_minute_rate', 'five_minute_rate',
                    'fifteen_minute_rate', 'mean_rate',
                    'min', 'max', 'mean', 'stddev'
                ], [
                    'median', 'percentile_95th'
                ])
            if isinstance(metric, Counter):
                self.log_metric(name, 'counter', metric, [
                    'count'
                ])
            if isinstance(metric, Histogram):
                self.log_metric(name, 'histogram', metric, [
                    'count', 'min', 'max', 'mean', 'stddev',
                ], [
                    'median', 'percentile_95th'
                ])

    def log_metric(self, name, type, metric, keys, snapshot_keys=None):
        if snapshot_keys is None:
            snapshot_keys = []
        messages = []
        if self.prefix:
            messages.append(self.prefix)

        messages.append(name)
        messages.append(type)

        for name in keys:
            messages.append("{0}={1}".format(name, getattr(metric, name)))

        if hasattr(metric, 'snapshot'):
            snapshot = metric.snapshot
            for name in snapshot_keys:
                messages.append("{0}={1}".format(name, getattr(snapshot, name)))

        self.logger.log(self.level, " ".join(messages))
