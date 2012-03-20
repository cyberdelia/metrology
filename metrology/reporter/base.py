from metrology.registry import registry
from metrology.utils.periodic import PeriodicTask


class Reporter(PeriodicTask):
    def __init__(self, interval=60, *args, **options):
        self.registry = options.get('registry', registry)
        super(Reporter, self).__init__(interval=interval)

    def task(self):
        self.write()

    def write(self):
        raise NotImplementedError
