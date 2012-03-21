from metrology.exceptions import ReporterException
from metrology.instruments import *  # noqa
from metrology.reporter.base import Reporter


class LibratoReporter(Reporter):
    def __init__(self, email, token, **options):
        self.email = email
        self.token = token

        try:
            import requests  # noqa
        except:
            raise ReporterException("Librato reporter requires the 'requests' library")

        self.source = options.get('source')
        self.prefix = options.get('prefix')
        super(LibratoReporter, self).__init__(**options)

    def write(self):
        for name, metric in self.registry:
            if isinstance(metric, Meter):
                self.send_metric(name, 'meter', metric, [
                    'count', 'one_minute_rate', 'five_minute_rate',
                    'fifteen_minute_rate', 'mean_rate'
                ])
            if isinstance(metric, Gauge):
                self.send_metric(name, 'gauge', metric, [
                    'value'
                ])
            if isinstance(metric, UtilizationTimer):
                self.send_metric(name, 'timer', metric, [
                    'count', 'one_minute_rate', 'five_minute_rate',
                    'fifteen_minute_rate', 'mean_rate',
                    'min', 'max', 'mean', 'stddev',
                    'one_minute_utilization', 'five_minute_utilization',
                    'fifteen_minute_utilization', 'mean_utilization'
                ], [
                    'median', 'percentile_95th'
                ])
            if isinstance(metric, Timer):
                self.send_metric(name, 'timer', metric, [
                    'count', 'one_minute_rate', 'five_minute_rate',
                    'fifteen_minute_rate', 'mean_rate',
                    'min', 'max', 'mean', 'stddev'
                ], [
                    'median', 'percentile_95th'
                ])
            if isinstance(metric, Counter):
                self.send_metric(name, 'counter', metric, [
                    'count'
                ])
            if isinstance(metric, Histogram):
                sef.send_metric(name, 'histogram', metric, [
                    'count', 'min', 'max', 'mean', 'stddev',
                ], [
                    'median', 'percentile_95th'
                ])

    def send_write(self, name, type, metric, keys, snapshot_keys=[]):
        base_name = re.sub(r"\s+", "_", name)
        if self.prefix:
            base_name = "{0}.{1}".format(self.prefix, base_name)

        for name in keys:
            pass

        if hasattr(metric, 'snapshot'):
            snapshot = metric.snapshot
            for name in snapshot_keys:
                pass
