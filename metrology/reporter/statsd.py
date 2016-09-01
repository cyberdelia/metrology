import socket
import sys

from metrology.instruments import *  # noqa
from metrology.reporter.base import Reporter


class StatsDReporter(Reporter):
    """
    A statsd reporter that sends metrics to statsd daemon ::

      reporter = StatsDReporter('statsd.local', 8125)
      reporter.start()

    :param host: hostname of statsd daemon
    :param port: port of daemon
    :param interval: time between each reports
    :param prefix: metrics name prefix
    """
    def __init__(self, host, port, conn_type='udp', **options):
        self.host = host
        self.port = port
        self.conn_type = conn_type

        self.prefix = options.get('prefix')
        self.batch_size = options.get('batch_size', 100)
        self.batch_buffer = ''
        if self.batch_size <= 0:
            self.batch_size = 1
        self._socket = None
        super(StatsDReporter, self).__init__(**options)
        self.batch_count = 0
        if conn_type == 'tcp':
            self._send = self._send_tcp
        else:
            self._send = self._send_udp

        self.translate_dict = {'meter': 'm', 'gauge': 'g',
                               'timer': 'ms', 'counter': 'c',
                               'histogram': 'h'}

    @property
    def socket(self):
        if not self._socket:
            if self.conn_type == 'tcp':
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.connect((self.host, self.port))
            else:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return self._socket

    def write(self):
        for name, metric in self.registry:
            if isinstance(metric, Meter):
                self.send_metric(name, 'meter', metric, 'count')
            if isinstance(metric, Gauge):
                self.send_metric(name, 'gauge', metric, 'value')
            if isinstance(metric, UtilizationTimer):
                self.send_metric(name, 'timer', metric, 'mean')
            if isinstance(metric, Timer):
                self.send_metric(name, 'timer', metric, 'mean')
            if isinstance(metric, Counter):
                self.send_metric(name, 'counter', metric, 'count')
            if isinstance(metric, Histogram):
                self.send_metric(name, 'histogram', metric, 'mean')

        self._send()

    def send_metric(self, name, mtype, metric, keys):
        value = getattr(metric, keys, None)
        if value:
            self._buffered_send_metric(name, value, mtype)

    def _buffered_send_metric(self, name, value, mtype):
        if self.prefix:
            name = '{0}.{1}'.format(self.prefix, name)

        self.batch_count += 1
        if mtype in self.translate_dict:
            mtype = self.translate_dict[mtype]
        else:
            mtype = 'g'

        self.batch_buffer += '{0}:{1}|{2}\n'.format(
            name, value, mtype
        )

        if self.batch_count >= self.batch_size:
            self._send()

    def _send_tcp(self):
        if len(self.batch_buffer):
            if sys.version_info[0] > 2:
                self.socket.sendall(bytes(self.batch_buffer, 'ascii'))
            else:
                self.socket.sendall(self.batch_buffer)

            self.batch_count = 0
            self.batch_buffer = ''

    def _send_udp(self):
        if len(self.batch_buffer):
            if sys.version_info[0] > 2:
                self.socket.sendto(bytes(self.batch_buffer, 'ascii'),
                                   (self.host, self.port))
            else:
                self.socket.sendto(self.batch_buffer,
                                   (self.host, self.port))

            self.batch_count = 0
            self.batch_buffer = ''
