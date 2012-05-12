class MetrologyException(Exception):
    pass


class RegistryException(MetrologyException):
    pass


class ArgumentException(MetrologyException):
    pass


class ReporterException(MetrologyException):
    pass
