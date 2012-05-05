import inspect

from threading import RLock

from metrology.instruments import Counter, Meter, Timer, UtilizationTimer, HistogramUniform


class Registry(object):
    def __init__(self):
        self.lock = RLock()
        self.metrics = {}

    def clear(self):
        with self.lock:
            for key, metric in list(self.metrics.items()):
                if hasattr(metric, 'stop'):
                    metric.stop()
        self.metrics = {}

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

    def histogram(self, name, klass=None):
        if not klass:
            klass = HistogramUniform
        return self.add_or_get(name, klass)

    def get(self, name):
        with self.lock:
            return self.metrics[name]

    def add(self, name, metric):
        with self.lock:
            if name in self.metrics:
                raise
            else:
                self.metrics[name] = metric

    def add_or_get(self, name, klass):
        with self.lock:
            if name in self.metrics:
                metric = self.metrics[name]
                if not isinstance(metric, klass):
                    raise
                else:
                    return metric
            else:
                if inspect.isclass(klass):
                    self.metrics[name] = klass()
                else:
                    self.metrics[name] = klass
                return self.metrics[name]

    def stop(self):
        self.clear()

    def __iter__(self):
        with self.lock:
            for name, metric in list(self.metrics.items()):
                yield name, metric

registry = Registry()
