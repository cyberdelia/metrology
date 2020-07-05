import inspect

from threading import RLock
from collections import defaultdict

from metrology.exceptions import RegistryException
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
        self.metrics_by_tag = defaultdict(lambda: [])
        self.tags_by_metric = {}

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
        name = safe_key(name)
        with self.lock:
            return self.metrics[name]

    def add(self, name, metric):
        key = safe_key(name)
        with self.lock:
            if key in self.metrics:
                raise RegistryException("{0} already present "
                                        "in the registry.".format(name))
            else:
                self.metrics[key] = metric
                self._index(name, metric)

    def add_or_get(self, name, klass):
        """Creates an instance of `klass`, and registered it with `name`.
        `klass` may also be an instance of a metric, and will be registered
        directly.

        If `name` is already registered:

        - If a klass is passed, return the existing instance.
        - If an instance is passed, replace the existing metric with the new
          instance.
        """
        key = safe_key(name)
        with self.lock:
            metric = self.metrics.get(key)

            if metric is not None:
                # If a klass was given, return the existing metric.
                if inspect.isclass(klass):
                    if not isinstance(metric, klass):
                        raise RegistryException("{0} is not of "
                                                "type {1}.".format(name, klass))
                    return metric

                # If a metric object was passed, make sure the registry has
                # the most recent version.
                else:
                    self.metrics[key] = klass
                    self._index(name, klass)

            else:
                if inspect.isclass(klass):
                    metric = klass()
                else:
                    metric = klass
                self.metrics[key] = metric
                self._index(name, metric)
                return metric

    def _index(self, name, metric):
        if not isinstance(name, dict):
            return

        for key, value in name.items():
            self.metrics_by_tag[(key, value)].append(metric)
        self.tags_by_metric[metric] = name

    def filter_metrics(self, filters):
        """
        Find all metrics matching the tags given in `filters`. For each
        metric, remain a 2-tuple (metric, other_tags).
        """
        result = None

        for filter_tag, filter_value in filters.items():
            local_match = set(self.metrics_by_tag[(filter_tag, filter_value)])
            if result is None:
                result = local_match
            else:
                result = result.intersection(local_match)

        for metric in result:
            tags = self.tags_by_metric[metric].copy()
            # Do not include any tags the caller has queried for
            for tag in filters:
                del tags[tag]
            yield metric, tags

    def stop(self):
        self.clear()

    def __iter__(self):
        with self.lock:
            for name, metric in self.metrics.items():
                yield name, metric


def safe_key(name):
    if isinstance(name, dict):
        return tuple(name.items())
    return name


registry = Registry()
