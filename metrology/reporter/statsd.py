import socket

from metrology.instruments import *  # noqa
from metrology.reporter.base import Reporter


class StatsdReporter(Reporter):
    def __init__(self, host, port, **options):
        self.host = host
        self.port = port
        self.addr = (host, port)

        self.prefix = options.get('prefix')
        super(StatsdReporter, self).__init__(**options)

    @property
    def socket(self):
        if not self._socket:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return self._socket

    def write(self):
        for name, metric in self.registry:
            pass
