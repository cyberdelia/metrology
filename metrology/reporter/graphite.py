import re
import socket
import pickle
import struct
import sys

from metrology.instruments import *  # noqa
from metrology.reporter.base import Reporter
from metrology.utils import now


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
        self.pickle = options.get('pickle', False)
        self.batch_size = options.get('batch_size', 100)
        if self.batch_size <= 0:
            self.batch_size = 1
        super(GraphiteReporter, self).__init__(**options)
        self.batch_count = 0
        if self.pickle:
            self._buffered_send_metric = self._buffered_pickle_send_metric
            self._send = self._send_pickle
            self.batch_buffer = []
        else:
            self._buffered_send_metric = self._buffered_plaintext_send_metric
            self._send = self._send_plaintext
            self.batch_buffer = ""

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
                    'median', 'percentile_95th', 'percentile_99th', 'percentile_999th'
                ])
            if isinstance(metric, Timer):
                self.send_metric(name, 'timer', metric, [
                    'count', 'total_time', 'one_minute_rate', 'five_minute_rate',
                    'fifteen_minute_rate', 'mean_rate',
                    'min', 'max', 'mean', 'stddev'
                ], [
                    'median', 'percentile_95th', 'percentile_99th', 'percentile_999th'
                ])
            if isinstance(metric, Counter):
                self.send_metric(name, 'counter', metric, [
                    'count'
                ])
            if isinstance(metric, Histogram):
                self.send_metric(name, 'histogram', metric, [
                    'count', 'min', 'max', 'mean', 'stddev',
                ], [
                    'median', 'percentile_95th', 'percentile_99th', 'percentile_999th'
                ])

        # Send metrics that might be in buffers
        self._send()

    def send_metric(self, name, type, metric, keys, snapshot_keys=None):
        if snapshot_keys is None:
            snapshot_keys = []
        base_name = re.sub(r"\s+", "_", name)
        if self.prefix:
            base_name = "{0}.{1}".format(self.prefix, base_name)

        for name in keys:
            value = True
            value = getattr(metric, name)
            self._buffered_send_metric(base_name, name, value, now())

        if hasattr(metric, 'snapshot'):
            snapshot = metric.snapshot
            for name in snapshot_keys:
                value = True
                value = getattr(snapshot, name)
                self._buffered_send_metric(base_name, name, value, now())

    def _buffered_plaintext_send_metric(self, base_name, name, value, t, force=False):
        self.batch_count += 1
        self.batch_buffer += "{0}.{1} {2} {3}\n".format(
            base_name, name, value, now())
        # Check if we reach batch size and send
        if self.batch_count >= self.batch_size:
            self._send_plaintext()

    def _buffered_pickle_send_metric(self, base_name, name, value, t):
        self.batch_count += 1
        self.batch_buffer.append(("{0}.{1}".format(base_name, name), (t, value)))
        # Check if we reach batch size and send
        if self.batch_count >= self.batch_size:
            self._send_pickle()

    def _send_plaintext(self):
        if len(self.batch_buffer):
            if sys.version_info[0] > 2:
                self.socket.sendall(bytes(self.batch_buffer + '\n', 'ascii'))
            else:
                self.socket.sendall(self.batch_buffer + "\n")
            # Reinitialze buffer and counter
            self.batch_count = 0
            self.batch_buffer = ""

    def _send_pickle(self):
        if len(self.batch_buffer):
            payload = pickle.dumps(self.batch_buffer)
            header = struct.pack("!L", len(payload))
            message = header + payload
            self.socket.sendall(message)
            # Reinitialze buffer and counter
            self.batch_count = 0
            self.batch_buffer = []
