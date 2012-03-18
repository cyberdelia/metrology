from atomic import Atomic


class Counter(object):
    def __init__(self):
        self._count = Atomic(0)

    def increment(self, value=1):
        self._count.value += value

    def decrement(self, value=1):
        self._count.value -= value

    def clear(self):
        self._count.value = 0

    @property
    def count(self):
        return self._count.value
