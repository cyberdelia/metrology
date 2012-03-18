# -*- flake8: noqa -*-
import time

from threading import Thread

from metrology.reporter.graphite import GraphiteReporter
from metrology.reporter.librato import LibratoReporter
from metrology.reporter.logger import LoggerReporter


class Reporter(Thread):
    def __init__(self, *args, **options):
        self.registry = options.get('registry', registry)
        self.interval = options.get('interval', 60)
        super(Reporter, self).__init__()

    def start(self):
        self.running = True
        super(Reporter, self).start()
    
    def stop(self):
        self.running = False
    
    def run(self):
        while self.running:
            time.sleep(self.interval)
            self.write()

    def write(self):
        raise NotImplementedError
