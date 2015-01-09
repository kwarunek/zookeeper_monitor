# -*- coding:utf-8 -*-
import os
import anyconfig
from tornado import gen, web


class BaseHandler(web.RequestHandler):
    """ Handles json request for cluster data """
    ACTION = 'r'

    def get_template_path(self):
        self.root_path = os.path.dirname(__file__)
        return os.path.join(self.root_path, 'front/template/')


    @gen.coroutine
    def get(self, param=None):  # pylint: disable=W0221
        """ GET handler

        Gets data, dumps to json and send with proper json mime.
        """
        action = getattr(self, 'get_{}_data'.format(self.ACTION))
        res = yield action(param)
        json = anyconfig.dumps(res, 'json')
        self.set_header('Content-Type', 'application/json')
        self.write(json)
        self.finish()

    @gen.coroutine
    def get_cluster_data(self, param=None):  # pylint: disable=W0613
        """ Cluster data provider

        Returns:
            Dict with host data
        """
        data = {}
        cluster = self.application.get_cluster()
        data['name'] = str(cluster)
        data['hosts'] = []
        for host in cluster.get_hosts():
            yield host.srvr()
            info = yield host.get_info()
            info['cluster'] = str(info['cluster'])
            data['hosts'].append(info)
        raise gen.Return(data)

    @gen.coroutine
    def get_host_data(self, zhost):
        """ Host stat provider

        Args:
            zhost (string): IP and port of host in cluster. Should be delimited by : or -

              Example:
                  127.0.0.1-2181
        Returns:
            Dict with host data
        """
        cluster = self.application.get_cluster()
        zhost = zhost.replace('-', ':')  # allow w/o escaping issue
        host = cluster.get_host(zhost)
        stat = yield host.stat()
        info = yield host.get_info()
        raise gen.Return({'stat': stat, 'info': info})


class JsonClusterHandler(BaseHandler):
    """ Handles json request for cluster data """
    ACTION = 'cluster'


class JsonHostHandler(BaseHandler):
    """ Handles json request for host data """
    ACTION = 'host'


class HtmlClusterHandler(BaseHandler):
    """ Handles only html and sets appropriate JS param """
    ACTION = 'cluster'

    @gen.coroutine
    def get(self, param=None):
        """ GET handler

        Gets data and renders it.
        """
        action = getattr(self, 'get_{}_data'.format(self.ACTION))
        res = yield action(param)
        self.render('{}.html'.format(self.ACTION), data=res)


class HtmlHostHandler(HtmlClusterHandler):
    """ Handles only html and sets appropriate JS param """
    ACTION = 'host'
