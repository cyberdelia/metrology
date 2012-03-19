from metrology.reporter.base import Reporter


class GraphiteReporter(Reporter):
    def __init__(self, host, port, **options):
        self.host = host
        self.port = port

        self.prefix = options.get('prefix')
        super(GraphiteReporter, self).__init__(**options)

    def write(self):
        for name, metric in self.registry:
            pass
