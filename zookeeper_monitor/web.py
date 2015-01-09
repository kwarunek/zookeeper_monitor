# -*- coding:utf-8 -*-
""" Command line runner, tornado-based webserver
"""
import anyconfig
import argparse
import logging
import os
import signal
import tornado.web
from tornado.ioloop import IOLoop
from .handlers import HtmlHostHandler, HtmlClusterHandler, JsonClusterHandler, JsonHostHandler
from .zk import Cluster
from .version import __app__, __version__


class App(object):
    """ Command line app

        This class configure WebMonitor from command line parameters
    """

    def __init__(self, ioloop=None):
        self.webmonitor = WebMonitor()
        self.args = None
        self.ioloop = ioloop or IOLoop.instance()

    def configure(self):
        """ Configures server

        Handles command line parameters, merge with defaults and invokes setting up cluster
        """
        parser = argparse.ArgumentParser(description='Web-based monitor for zookeeper.', prog=__app__)
        parser.add_argument('-i', '--ip', action="store", dest='ip', default='127.0.0.1',
                            help='Address to bind to. Default 127.0.0.1')
        parser.add_argument('-p', '--port', action="store", dest='port', default=8080, type=int,
                            help='Port to listen on. Default 8080.')
        parser.add_argument('--config', '-c', action='store', dest='config',
                            help='Config file contaning clusters to view. If not provided, localhost will be used.')
        parser.add_argument('-v', '--version', action='version', version='{} {}'.format(__app__, __version__))
        self.args = parser.parse_args()

        if self.args.config:
            logging.info('Using config file: %s', self.args.config)
            self.webmonitor.load_config_from_file(self.args.config)
        else:
            logging.info('Connecting to localhost:2181')
            self.webmonitor.set_cluster({'name': 'default', 'hosts': [{'addr': 'localhost', 'port': 2181}]})

    def start_server(self):
        """ Starts Tornado server """
        self.webmonitor.listen(self.args.port, address=self.args.ip)
        print('Starting web monitor at http://{}:{}'.format(self.args.ip, self.args.port))
        signal.signal(
            signal.SIGINT,
            lambda sig, frame: self.ioloop.instance().add_callback_from_signal(self.on_shutdown)
        )
        self.ioloop.instance().start()

    def on_shutdown(self):
        """ SIGINT handler - proper way to stop """
        print('Shutting down')
        self.ioloop.instance().stop()


class WebMonitor(tornado.web.Application):
    """ Tornado based server

    Serves www interface.
    """

    def __init__(self):

        handlers = [
            (r'/(favicon.png)', tornado.web.StaticFileHandler, {'path': self._get_path('static')}),
            (r'/cluster\.json', JsonClusterHandler),
            (r'/cluster/host/(?P<param>[^\/]+)\.json', JsonHostHandler),
            (r'/cluster/host/(?P<param>[^\/]+)', HtmlHostHandler),
            (r'/cluster', HtmlClusterHandler),
            (r"/", HtmlClusterHandler),
        ]

        self._cluster = None
        tornado.web.Application.__init__(
            self, handlers, debug=True,
            static_path=self._get_path('static'),
            template_path=self._get_path('template')
        )

    def _get_path(self, resource):
        self.root_path = os.path.dirname(__file__)
        return os.path.join(self.root_path, 'front/{}/'.format(resource))

    def load_config_from_file(self, config_file, force_format=None):
        """ Load config from file

        Args:
            config_file: Config's filename to be loaded
            f: Force config format ex. yaml, json
        """
        data = anyconfig.load(config_file, force_format)
        self.set_cluster(data)

    def set_cluster(self, data):
        """ Sets cluster and its hosts

        Args:
            data (dict): Configuration of cluster

              Example:

                {
                    "name": "brand-new-zookeeper-cluster",
                    "hosts": [
                       {"addr": "10.1.15.1", "port": 2181, "dc":"eu-west"},
                       {"addr": "10.1.31.2", "port": 2181, "dc":"eu-west"},
                       {"addr": "10.1.12.3", "port": 2181, "dc":"eu-west"}
                    ]
                }
        """
        cluster = Cluster(data['name'])
        for host in data['hosts']:
            cluster.add_host(**host)
        self._cluster = cluster

    def get_cluster(self):
        """ Gets cluster """
        return self._cluster


if __name__ == "__main__":
    commandline_app = App()
    commandline_app.configure()
    commandline_app.start_server()
