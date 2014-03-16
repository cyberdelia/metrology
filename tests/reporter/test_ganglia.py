from ganglia import GMetric

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch  # noqa

from unittest import TestCase

from metrology import Metrology
from metrology.reporter.ganglia import GangliaReporter


class GangliaReporterTest(TestCase):
    def setUp(self):
        self.reporter = GangliaReporter("Group Name", "localhost", 8649)

        Metrology.meter('meter').mark()
        Metrology.counter('counter').increment()
        Metrology.timer('timer').update(5)
        Metrology.utilization_timer('utimer').update(5)

    def tearDown(self):
        self.reporter.stop()
        Metrology.stop()

    @patch.object(GMetric, "send")
    def test_write(self, mock):
        self.reporter.write()
        self.assertTrue(mock.send.assert_called())
