import logging

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO  # noqa

from unittest import TestCase

from metrology import Metrology
from metrology.reporter.logger import LoggerReporter


class LoggerReporterTest(TestCase):
    def setUp(self):
        self.output = StringIO()
        logging.basicConfig(stream=self.output, level=logging.INFO)

        self.reporter = LoggerReporter()

        Metrology.meter('meter').mark()
        Metrology.counter('counter').increment()
        Metrology.timer('timer').update(1.5)
        Metrology.utilization_timer('utimer').update(1.5)

    def tearDown(self):
        self.reporter.stop()
        Metrology.stop()

    def test_write(self):
        self.reporter.write()
        self.assertTrue("median=" in self.output.getvalue())
