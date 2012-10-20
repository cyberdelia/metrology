try:
    from StringIO import StringIO
    from mock import patch
except ImportError:
    from io import StringIO  # noqa
    from unittest.mock import patch  # noqa

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
        Metrology.histogram('histogram').update(1.5)

    def tearDown(self):
        self.reporter.stop()
        Metrology.stop()

    @patch.object(GraphiteReporter, 'socket')
    def test_send(self, mock):
        self.reporter.write()
        self.assertTrue(mock.send.assert_called())
        self.assertEqual(50, len(mock.send.call_args_list))
