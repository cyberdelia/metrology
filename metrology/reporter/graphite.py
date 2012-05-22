import re
import socket
from time import time

from metrology.instruments import *  # noqa
from metrology.reporter.base import Reporter


class GraphiteReporter(Reporter):
    """
    A graphite reporter that send metrics to graphite ::

      reporter = GraphiteReporter('graphite.local', 2003)
      reporter.start()

    :param host: hostname of graphite
    :param port: port of graphite
    :param interval: time between each reporting
    :param prefix: metrics name prefix
    """
    def __init__(self, host, port, **options):
        self.host = host
        self.port = port

        self.prefix = options.get('prefix')
        super(GraphiteReporter, self).__init__(**options)

    @property
    def socket(self):
        if not hasattr(self, '_socket'):
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self.host, self.port))
        return self._socket

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

    def send_metric(self, name, type, metric, keys, snapshot_keys=None):
        if snapshot_keys is None:
            snapshot_keys = []
        base_name = re.sub(r"\s+", "_", name)
        if self.prefix:
            base_name = "{0}.{1}".format(self.prefix, base_name)

        for name in keys:
            value = getattr(metric, name)
            self.socket.send("{0}.{1} {2} {3}\n\n".format(
                base_name, name, value, int(time())
            ))

        if hasattr(metric, 'snapshot'):
            snapshot = metric.snapshot
            for name in snapshot_keys:
                value = getattr(snapshot, name)
                self.socket.send("{0}.{1} {2} {3}\n\n".format(
                    base_name, name, value, int(time())
                ))
