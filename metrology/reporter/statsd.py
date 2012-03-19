import logging

from metrology.instruments import *  # noqa
from metrology.reporter.base import Reporter


class StatsdReporter(Reporter):
    def __init__(self, logger=None, level=logging.INFO, **options):
        self.logger = logger
        self.level = level

        self.prefix = options.get('prefix')
        super(StatsdReporter, self).__init__(**options)

    def write(self):
        for name, metric in self.registry:
            if isinstance(metric, Meter):
                pass
            if isinstance(metric, Gauge):
                pass
