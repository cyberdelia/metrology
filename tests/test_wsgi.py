import requests
import threading

from unittest import TestCase
from wsgiref.simple_server import demo_app, make_server, WSGIRequestHandler

from metrology import Metrology
from metrology.wsgi import Middleware


class SilentWSGIHandler(WSGIRequestHandler):
    def log_message(*args):
        pass


class TestServer(object):
    def __init__(self, application):
        self.application = application
        self.server = make_server(
            '127.0.0.1', 0, application, handler_class=SilentWSGIHandler)

    def get(self, *args, **kwargs):
        return self.request('get', *args, **kwargs)

    def request(self, method, path, *args, **kwargs):
        url = 'http://{0[0]}:{0[1]}{1}'.format(self.server.server_address, path)
        thread = threading.Thread(target=self.server.handle_request)
        thread.start()
        response = requests.request(method, url, *args, **kwargs)
        thread.join()
        return response


class MiddlewareTest(TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize test application
        cls.application = Middleware(demo_app)
        cls.server = TestServer(cls.application)
        super(MiddlewareTest, cls).setUpClass()

    def tearDown(self):
        Metrology.stop()

    def test_request(self):
        self.server.get('/')
        self.assertEqual(1, Metrology.meter('request').count)
        self.assertEqual(1, Metrology.timer('request_time').count)
