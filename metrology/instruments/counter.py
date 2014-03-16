from atomic import AtomicLong


class Counter(object):
    """
    A counter is like a gauge, but you can increment or decrement its value ::

      counter = Metrology.counter('pending-jobs')
      counter.increment()
      counter.decrement()
      counter.count

    """
    def __init__(self):
        self._count = AtomicLong(0)

    def increment(self, value=1):
        """Increment the counter. By default it will increment by 1.

        :param value: value to increment the counter.
        """
        self._count += value

    def decrement(self, value=1):
        """Decrement the counter. By default it will decrement by 1.

        :param value: value to decrement the counter.
        """
        self._count -= value

    def clear(self):
        self._count.value = 0

    @property
    def count(self):
        """Return the current value of the counter."""
        return self._count.value
