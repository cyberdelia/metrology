from metrology.registry import registry


class Metrology(object):
    @classmethod
    def get(cls, name):
        return registry.get(name)

    @classmethod
    def counter(cls, name):
        return registry.counter(name)

    @classmethod
    def derive(cls, name):
        return registry.derive(name)

    @classmethod
    def meter(cls, name):
        return registry.meter(name)

    @classmethod
    def gauge(cls, name, gauge):
        return registry.gauge(name, gauge)

    @classmethod
    def timer(cls, name):
        return registry.timer(name)

    @classmethod
    def utilization_timer(cls, name):
        return registry.utilization_timer(name)

    @classmethod
    def histogram(cls, name, histogram=None):
        return registry.histogram(name, histogram)

    @classmethod
    def health_check(cls, name, health_check):
        return registry.health_check(name, health_check)

    @classmethod
    def profiler(cls, name):
        return registry.profiler(name)

    @classmethod
    def stop(cls):
        return registry.stop()
