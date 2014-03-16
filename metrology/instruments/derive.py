from atomic import AtomicLong

from metrology.instruments.meter import Meter
from metrology.stats import EWMA


class Derive(Meter):
    """
    A derive is like a meter but accepts an absolute counter as input.

      derive = Metrology.derive('network.io')
      derive.mark()
      derive.count

    """
    def __init__(self, average_class=EWMA):
        self.last = AtomicLong(0)
        super(Derive, self).__init__(average_class)

    def mark(self, value=1):
        """Record an event with the derive.

        :param value: counter value to record
        """
        last = self.last.get_and_set(value)
        if last <= value:
            value = value - last
        super(Derive, self).mark(value)
