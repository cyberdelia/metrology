import requests

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch  # noqa

from unittest import TestCase

from metrology import Metrology
from metrology.reporter.librato import LibratoReporter


class LibratoReporterTest(TestCase):
    def setUp(self):
        self.reporter = LibratoReporter("<email>", "<token>")

        Metrology.meter('meter').mark()
        Metrology.counter('counter').increment()
        Metrology.timer('timer').update(5)
        Metrology.utilization_timer({
                'name': 'utimer',
                'type': 'A'
            }).update(5)

    def tearDown(self):
        self.reporter.stop()
        Metrology.stop()

    @patch.object(requests, "post")
    def test_write(self, mock):
        self.reporter.write()
        self.assertTrue(mock.called)
        self.assertTrue("gauges" in mock.call_args_list[0][1]['data'])
        self.assertTrue("counters" in mock.call_args_list[0][1]['data'])
        self.assertTrue("tags" in mock.call_args_list[0][1]['data'])
        self.assertTrue("type" in mock.call_args_list[0][1]['data'])
