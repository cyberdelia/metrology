from metrology.registry import registry


class Metrology(object):
    @classmethod
    def get(cls, name):
        return registry.get(name)

    @classmethod
    def counter(cls, name):
        return registry.counter(name)

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
