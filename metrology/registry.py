import inspect

from threading import RLock

from metrology.exceptions import RegistryException, ArgumentException
from metrology.instruments import (
    Counter,
    Derive,
    HistogramUniform,
    Meter,
    Timer,
    UtilizationTimer
)


class Registry(object):
    def __init__(self):
        self.lock = RLock()
        self.metrics = {}

    def clear(self):
        with self.lock:
            for metric in self.metrics.values():
                if hasattr(metric, 'stop'):
                    metric.stop()
            self.metrics.clear()

    def counter(self, name):
        return self.add_or_get(name, Counter)

    def meter(self, name):
        return self.add_or_get(name, Meter)

    def gauge(self, name, klass):
        return self.add_or_get(name, klass)

    def timer(self, name):
        return self.add_or_get(name, Timer)

    def utilization_timer(self, name):
        return self.add_or_get(name, UtilizationTimer)

    def health_check(self, name, klass):
        return self.add_or_get(name, klass)

    def histogram(self, name, klass=None):
        if not klass:
            klass = HistogramUniform
        return self.add_or_get(name, klass)

    def derive(self, name):
        return self.add_or_get(name, Derive)

    def get(self, name):
        with self.lock:
            key = self._compose_key(name)
            return self.metrics[key]

    def add(self, name, metric):
        with self.lock:
            key = self._compose_key(name)
            if key in self.metrics:
                raise RegistryException("{0} already present "
                                        "in the registry.".format(name))
            else:
                self.metrics[key] = metric

    def add_or_get(self, name, klass):
        with self.lock:
            key = self._compose_key(name)
            metric = self.metrics.get(key)
            if metric is not None:
                if not isinstance(metric, klass):
                    raise RegistryException("{0} is not of "
                                            "type {1}.".format(name, klass))
            else:
                if inspect.isclass(klass):
                    metric = klass()
                else:
                    metric = klass
                self.metrics[key] = metric
            return metric

    def stop(self):
        self.clear()

    def _compose_key(self, name):
        if isinstance(name, dict):
            if 'name' not in name:
                raise ArgumentException('Tagged metric needs a name entry: '
                                        + str(name))
        else:
            name = {'name': name}
        return frozenset(name.items())

    def _decompose_key(self, key):
        key = dict(key)
        name = key.pop('name')
        return (name, key if len(key) > 0 else None)

    def __iter__(self):
        with self.lock:
            for key, metric in self.metrics.items():
                key = dict(key)
                yield key['name'], metric

    @property
    def with_tags(self):
        with self.lock:
            for key, metric in self.metrics.items():
                key = self._decompose_key(key)
                yield key, metric


registry = Registry()
