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
        pass

    def tearDown(self):
        Metrology.stop()

    @patch.object(GraphiteReporter, 'socket')
    def test_send_nobatch(self, mock):
        self.reporter = GraphiteReporter('localhost', 3334, pickle=True, batch_size=1)

        Metrology.meter('meter').mark()
        Metrology.counter('counter').increment()
        Metrology.timer('timer').update(5)
        Metrology.utilization_timer('utimer').update(5)
        Metrology.histogram('histogram').update(5)
        self.reporter.write()
        self.assertTrue(mock.sendall.assert_called())
        self.assertEqual(50, len(mock.sendall.call_args_list))
        self.reporter.stop()

    @patch.object(GraphiteReporter, 'socket')
    def test_send_batch(self, mock):
        self.reporter = GraphiteReporter('localhost', 3334, pickle=True, batch_size=2)

        Metrology.meter('meter').mark()
        Metrology.counter('counter').increment()
        Metrology.timer('timer').update(5)
        Metrology.utilization_timer('utimer').update(5)
        Metrology.histogram('histogram').update(5)
        self.reporter.write()
        self.assertTrue(mock.sendall.assert_called())
        self.assertEqual(25, len(mock.sendall.call_args_list))
        self.reporter.stop()
