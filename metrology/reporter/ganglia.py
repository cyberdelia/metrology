from __future__ import absolute_import
from ganglia import GMetric

from metrology.instruments.counter import Counter
from metrology.instruments.gauge import Gauge
from metrology.instruments.histogram import Histogram
from metrology.instruments.meter import Meter
from metrology.reporter.base import Reporter


class GangliaReporter(Reporter):
    """
    A ganglia reporter that send metrics to ganglia ::

      reporter = GangliaReporter('Report Group Name', 'localhost', 8649, 'udp', interval=60)
      reporter.start()

    :param default_group_name: default group name for ganglia
    :param host: hostname of gmond
    :param port: port of gmond
    :param protocol: protocol for gmond sockets
    :param interval: time between each reporting
    """

    def __init__(self, default_group_name, host, port, protocol="udp", *args, **kwargs):
        super(GangliaReporter, self).__init__(*args, **kwargs)
        self.default_group_name = default_group_name
        self.gmetric = GMetric("{0}://{1}:{2}".format(protocol, host, port))
        self.groups = {}

    def set_group(self, metric_name, group_name):
        """Override the group name for certain metrics."""
        self.groups[metric_name] = group_name

    def write(self):
        for name, metric in self.registry:
            if isinstance(metric, Meter):
                self.send(name, 'Count', metric.count, 'int32', 'count')
                self.send(name, 'One Minute Rate', metric.one_minute_rate, 'double', 'per second')
                self.send(name, 'Five Minute Rate', metric.five_minute_rate, 'double', 'per second')
                self.send(name, 'Fifteen Minute Rate', metric.fifteen_minute_rate, 'double', 'per second')
                self.send(name, 'Mean Rate', metric.mean_rate, 'double', 'per second')
            elif isinstance(metric, Gauge):
                self.send(name, 'Value', metric.value(), 'int32', 'value')
            elif isinstance(metric, Histogram):
                self.send(name, 'Count', metric.count, 'int32', 'count')
                self.send(name, 'Mean value', metric.mean, 'double', 'mean value')
                self.send(name, 'Variance', metric.variance, 'double', 'variance')
            elif isinstance(metric, Counter):
                self.send(name, 'Count', metric.count, 'int32', 'count')

    def send(self, name, tracker, value, kind, unit):
        if tracker:
            name = "{0} - {1}".format(name, tracker)
        group = self.groups.get(name, self.default_group_name)
        self.gmetric.send(name=name, value=value, type=kind, units=unit, group=group)
