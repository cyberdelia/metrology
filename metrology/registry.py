import inspect

from threading import RLock

from metrology.exceptions import RegistryException
from metrology.instruments import Counter, Derive, Meter, Timer, UtilizationTimer, HistogramUniform


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
            return self.metrics[name]

    def add(self, name, metric):
        with self.lock:
            if name in self.metrics:
                raise RegistryException("{0} already present in the registry.".format(name))
            else:
                self.metrics[name] = metric

    def add_or_get(self, name, klass):
        with self.lock:
            metric = self.metrics.get(name)
            if metric is not None:
                if not isinstance(metric, klass):
                    raise RegistryException("{0} is not of type {1}.".format(name, klass))
            else:
                if inspect.isclass(klass):
                    metric = klass()
                else:
                    metric = klass
                self.metrics[name] = metric
            return metric

    def stop(self):
        self.clear()

    def __iter__(self):
        with self.lock:
            for name, metric in self.metrics.items():
                yield name, metric

registry = Registry()
