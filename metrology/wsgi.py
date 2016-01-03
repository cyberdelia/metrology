from metrology import Metrology


class Middleware(object):
    """
    A WSGI middleware to measure requests rate and time ::

        application = Middleware(application, reporter)

    :param application: your wsgi application
    :param reporter: your metrology reporter
    """
    def __init__(self, application, reporter=None, **kwargs):
        self.application = application
        self.request = Metrology.meter('request')
        self.request_time = Metrology.timer('request_time')

        # Start reporter
        if reporter:
            reporter.start()

    def __call__(self, environ, start_response):
        self.request.mark()
        with self.request_time:
            return self.application(environ, start_response)
