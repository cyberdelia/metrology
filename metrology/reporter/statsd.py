import functools
import socket
import sys

from metrology.instruments import (
        Counter,
        Gauge,
        Histogram,
        Meter,
        Timer,
        UtilizationTimer
)
from metrology.reporter.base import Reporter


def class_name(obj):
    return obj.__name__ if isinstance(obj, type) else type(obj).__name__


def mmap(func, iterable):
    """Wrapper to make map() behave the same on Py2 and Py3."""

    if sys.version_info[0] > 2:
        return [i for i in map(func, iterable)]
    else:
        return map(func, iterable)


# NOTE(romcheg): This dictionary maps metric types to specific configuration
#                of the metric serializer.
#                Format:
#                    {
#                     'metric_type':
#                          {
#                             'serialized_type': str,
#                             'keys': list(str),
#                             'snapshot_keys': list(str)
#                          }
#                    }
SERIALIZER_CONFIG = {
    class_name(Meter): {
        'serialized_type': 'm',
        'keys': [
            'count', 'one_minute_rate', 'five_minute_rate', 'mean_rate',
            'fifteen_minute_rate'
            ],
        'snapshot_keys': None
        },

    class_name(Gauge): {
        'serialized_type': 'g',
        'keys': ['value'],
        'snapshot_keys': None
        },

    class_name(UtilizationTimer): {
        'serialized_type': 'ms',
        'keys': [
            'count', 'one_minute_rate', 'five_minute_rate', 'min', 'max',
            'fifteen_minute_rate', 'mean_rate', 'mean', 'stddev',
            'one_minute_utilization', 'five_minute_utilization',
            'fifteen_minute_utilization', 'mean_utilization'
            ],
        'snapshot_keys': [
            'median', 'percentile_95th', 'percentile_99th', 'percentile_999th'
            ]
        },

    class_name(Timer): {
        'serialized_type': 'ms',
        'keys': [
            'count', 'total_time', 'one_minute_rate', 'five_minute_rate',
            'fifteen_minute_rate', 'mean_rate', 'min', 'max', 'mean', 'stddev'
            ],
        'snapshot_keys': [
            'median', 'percentile_95th', 'percentile_99th', 'percentile_999th'
            ]
        },

    class_name(Counter): {
        'serialized_type': 'c',
        'keys': ['count'],
        'snapshot_keys': None
        },

    class_name(Histogram): {
        'serialized_type': 'h',
        'keys': ['count', 'min', 'max', 'mean', 'stddev'],
        'snapshot_keys': [
            'median', 'percentile_95th', 'percentile_99th', 'percentile_999th'
            ]
        }
}


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

    @property
    def socket(self):
        if not self._socket:
            if self.conn_type == 'tcp':
                self._socket = socket.socket(socket.AF_INET,
                                             socket.SOCK_STREAM)
                self._socket.connect((self.host, self.port))
            else:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return self._socket

    def write(self):
        for name, metric in self.registry:

            if self._is_metric_supported(metric):
                self.send_metric(name, metric)

        self._send()

    def send_metric(self, name, metric):
        """Send metric and its snapshot."""
        config = SERIALIZER_CONFIG[class_name(metric)]

        mmap(
            self._buffered_send_metric,
            self.serialize_metric(
                metric,
                name,
                config['keys'],
                config['serialized_type']
            )
        )

        if hasattr(metric, 'snapshot') and config.get('snapshot_keys'):
            mmap(
                self._buffered_send_metric,
                self.serialize_metric(
                    metric.snapshot,
                    name,
                    config['snapshot_keys'],
                    config['serialized_type']
                )
            )

    def serialize_metric(self, metric, m_name, keys, m_type):
        """Serialize and send available measures of a metric."""

        return [
            self.format_metric_string(m_name, getattr(metric, key), m_type)
            for key in keys
        ]

    def format_metric_string(self, name, value, m_type):
        """Compose a statsd compatible string for a metric's measurement."""

        # NOTE(romcheg): This serialized metric template is based on
        #                statsd's documentation.
        template = '{name}:{value}|{m_type}\n'

        if self.prefix:
            name = "{prefix}.{m_name}".format(prefix=self.prefix, m_name=name)

        return template.format(name=name, value=value, m_type=m_type)

    def _buffered_send_metric(self, metric_str):
        """Add a metric to the buffer."""

        self.batch_count += 1

        self.batch_buffer += metric_str

        # NOTE(romcheg): Send metrics if the number of metrics in the buffer
        #                has reached the threshold for sending.
        if self.batch_count >= self.batch_size:
            self._send()

    def _is_metric_supported(self, metric):
        return class_name(metric) in SERIALIZER_CONFIG

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
