import re

from json import dumps

from metrology.exceptions import ReporterException
from metrology.instruments import *  # noqa
from metrology.reporter.base import Reporter
from metrology.utils import now


class LibratoReporter(Reporter):
    """
    A librato metrics reporter that send metrics to librato ::

        reporter = LibratoReporter("<email>", "<token>", source="front.local")
        reporter.start()

    :param email: your librato email
    :param token: your librato api token
    :param source: source of the metric
    :param interval: time between each reporting
    :param prefix: metrics name prefix
    :param filters: allow given keys to be send
    :param excludes: exclude given keys to be send
    """
    def __init__(self, email, token, **options):
        self.email = email
        self.token = token

        try:
            import requests  # noqa
        except:
            raise ReporterException("Librato reporter requires the 'requests' library")

        self.filters = options.get('filters')
        self.excludes = options.get('excludes')
        self.source = options.get('source')
        self.prefix = options.get('prefix')
        super(LibratoReporter, self).__init__(**options)

    def list_metrics(self):
        for name, metric in self.registry:
            if isinstance(metric, Meter):
                yield self.prepare_metric(name, 'meter', metric, [
                    'count', 'one_minute_rate', 'five_minute_rate',
                    'fifteen_minute_rate', 'mean_rate'
                ])
            if isinstance(metric, Gauge):
                yield self.prepare_metric(name, 'gauge', metric, [
                    'value'
                ])
            if isinstance(metric, UtilizationTimer):
                yield self.prepare_metric(name, 'timer', metric, [
                    'count', 'one_minute_rate', 'five_minute_rate',
                    'fifteen_minute_rate', 'mean_rate',
                    'min', 'max', 'mean', 'stddev',
                    'one_minute_utilization', 'five_minute_utilization',
                    'fifteen_minute_utilization', 'mean_utilization'
                ], [
                    'median', 'percentile_95th'
                ])
            if isinstance(metric, Timer):
                yield self.prepare_metric(name, 'timer', metric, [
                    'count', 'total_time', 'one_minute_rate', 'five_minute_rate',
                    'fifteen_minute_rate', 'mean_rate',
                    'min', 'max', 'mean', 'stddev'
                ], [
                    'median', 'percentile_95th'
                ])
            if isinstance(metric, Counter):
                yield self.prepare_metric(name, 'counter', metric, [
                    'count'
                ])
            if isinstance(metric, Histogram):
                yield self.prepare_metric(name, 'histogram', metric, [
                    'count', 'min', 'max', 'mean', 'stddev',
                ], [
                    'median', 'percentile_95th'
                ])

    def write(self):
        import requests
        metrics = {
            "gauges": [data for metric in self.list_metrics() for type, data in metric if type == "gauge"],
            "counters": [data for metric in self.list_metrics() for type, data in metric if type == "counter"]
        }
        requests.post("https://metrics-api.librato.com/v1/metrics",
                      data=dumps(metrics),
                      auth=(self.email, self.token),
                      headers={'content-type': 'application/json'})

    def prepare_metric(self, name, type, metric, keys, snapshot_keys=[]):
        base_name = re.sub(r"\s+", "_", name)
        if self.prefix:
            base_name = "{0}.{1}".format(self.prefix, base_name)

        time = now()
        type = "gauge" if type != "counter" else "counter"

        if self.filters:
            keys = filter(lambda key: key in self.filters, keys)
            snapshot_keys = filter(lambda key: key in self.filters, snapshot_keys)

        if self.excludes:
            keys = filter(lambda key: key not in self.excludes, keys)
            snapshot_keys = filter(lambda key: key in self.excludes, snapshot_keys)

        for name in keys:
            value = getattr(metric, name)
            yield type, {
                "name": "{0}.{1}".format(base_name, name),
                "source": self.source,
                "time": time,
                "value": value
            }

        if hasattr(metric, 'snapshot'):
            snapshot = metric.snapshot
            for name in snapshot_keys:
                value = getattr(snapshot, name)
                yield type, {
                    "name": "{0}.{1}".format(base_name, name),
                    "source": self.source,
                    "time": time,
                    "value": value
                }
