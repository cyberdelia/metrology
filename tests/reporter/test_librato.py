import requests

from mock import patch
from unittest import TestCase

from metrology import Metrology
from metrology.reporter.librato import LibratoReporter


class LibratoReporterTest(TestCase):
    def setUp(self):
        self.reporter = LibratoReporter("<email>", "<token>")

        Metrology.meter('meter').mark()
        Metrology.counter('counter').increment()
        Metrology.timer('timer').update(1.5)
        Metrology.utilization_timer('utimer').update(1.5)

    def tearDown(self):
        self.reporter.stop()
        Metrology.stop()

    @patch.object(requests, "post")
    def test_write(self, mock):
        self.reporter.write()
        self.assertTrue(mock.send.assert_called())
        self.assertTrue("gauges" in mock.call_args_list[0][1]['data'])
        self.assertTrue("counters" in mock.call_args_list[0][1]['data'])
