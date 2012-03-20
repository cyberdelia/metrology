try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from mock import patch
from unittest import TestCase

from metrology import Metrology
from metrology.reporter.graphite import GraphiteReporter


class GraphiteReporterTest(TestCase):
    def setUp(self):
        self.reporter = GraphiteReporter('localhost', 3333)

        Metrology.meter('meter').mark()
        Metrology.counter('counter').increment()
        Metrology.timer('timer').update(1.5)
        Metrology.utilization_timer('utimer').update(1.5)

    def tearDown(self):
        self.reporter.stop()
        Metrology.stop()

    @patch.object(GraphiteReporter, 'socket') 
    def test_send(self, mock):
        self.reporter.write()
        self.assertTrue(mock.send.assert_called())
        self.assertTrue("utimer.count 1" in mock.send.call_args_list[0][0][0])
