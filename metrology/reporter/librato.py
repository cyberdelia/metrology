from metrology.exceptions import ReporterException
from metrology.instruments import *  # noqa
from metrology.reporter.base import Reporter


class LibratoReporter(Reporter):
    def __init__(self, email, token, **options):
        self.email = email
        self.token = token

        try:
            import requests  # noqa
        except:
            raise ReporterException("Librato reporter requires the 'requests' library")

        self.source = options.get('source')
        self.prefix = options.get('prefix')
        super(LibratoReporter, self).__init__(**options)

    def write(self):
        for name, metric in self.registry:
            pass
