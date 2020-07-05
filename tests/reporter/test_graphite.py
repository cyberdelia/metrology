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
    def tearDown(self):
        Metrology.stop()

    @patch.object(GraphiteReporter, 'socket')
    def test_send_nobatch(self, mock):
        self.reporter = GraphiteReporter('localhost', 3333, batch_size=1)

        Metrology.meter('meter').mark()
        Metrology.counter('counter').increment()
        Metrology.timer('timer').update(5)
        Metrology.utilization_timer('utimer').update(5)
        Metrology.histogram('histogram').update(5)
        self.reporter.write()
        self.assertTrue(mock.sendall.called)
        self.assertEqual(60, len(mock.sendall.call_args_list))
        self.reporter.stop()

    @patch.object(GraphiteReporter, 'socket')
    def test_send_batch(self, mock):
        self.reporter = GraphiteReporter('localhost', 3333, batch_size=2)

        Metrology.meter('meter').mark()
        Metrology.counter('counter').increment()
        Metrology.timer('timer').update(5)
        Metrology.utilization_timer('utimer').update(5)
        Metrology.histogram('histogram').update(5)
        self.reporter.write()
        self.assertTrue(mock.sendall.called)
        self.assertEqual(30, len(mock.sendall.call_args_list))
        self.reporter.stop()

    @patch.object(GraphiteReporter, 'socket')
    def test_metric_w_tags(self, mock):
        self.reporter = GraphiteReporter('localhost', 3333, batch_size=1)

        Metrology.meter({
                "name": "meter",
                "type": "A",
                "category": "B"
            }).mark()

        self.reporter.write()
        self.assertTrue(mock.sendall.called)
        sent_text = ''.join(call[0][0].decode("ascii")
                            for call in mock.sendall.call_args_list)
        self.assertIn("meter.count;", sent_text)
        self.assertIn(";type=A", sent_text)
        self.assertIn(";category=B", sent_text)
        self.reporter.stop()

    @patch.object(GraphiteReporter, 'socket')
    def test_sanitize_metric(self, mock):
        self.reporter = GraphiteReporter('localhost', 3333, batch_size=1)

        Metrology.meter('test.{met"er)|').mark()

        self.reporter.write()
        self.assertTrue(mock.sendall.called)
        sent_text = ''.join(call[0][0].decode("ascii")
                            for call in mock.sendall.call_args_list)
        self.assertIn("test._met_er_", sent_text)
        self.reporter.stop()

    @patch.object(GraphiteReporter, 'socket')
    def test_sanitize_metric_w_tags(self, mock):
        self.reporter = GraphiteReporter('localhost', 3333, batch_size=1)

        Metrology.meter({
                "name": "meter",
                "typ;e=": "~A"
            }).mark()

        Metrology.meter({
                "name": "meter2",
                "": ""
            }).mark()

        self.reporter.write()
        self.assertTrue(mock.sendall.called)
        sent_text = ''.join(call[0][0].decode("ascii")
                            for call in mock.sendall.call_args_list)
        self.assertIn("typ_e_=_A", sent_text)
        self.assertIn("empty_tag=empty_value", sent_text)
        self.reporter.stop()
