from metrology.reporter import Reporter


class LibratoReporter(Reporter):
    def __init__(self, email, token, **options):
        self.email = email
        self.token = token

        self.prefix = options.get('prefix')
        super(LibratoReporter, self).__init__(**options)

    def write(self):
        for name, metric in self.registry:
            pass
