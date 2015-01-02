# -*- coding:utf-8 -*-
""" Cluster represents group of connected host (zookeeper servers).

Example:

    cluster = Cluster('Some_name')
    cluster.add_host(addr='1.1.12.12')

    another_host = Host('localhost', 5555)
    cluster.add_host(another_host)

    yield cluster.get_host('1.1.12.12:2181').srvr()
    yield cluster.get_host(str(another_host)).srvr()
    # or
    yield cluster.get_host('localhost:5555').srvr()


"""
from .host import Host
from .exceptions import ClusterHostAddError, ClusterHostDuplicateError, ClusterHostCreateError


class Cluster(object):

    def __init__(self, name):
        """ Create cluster

        Args:
            name: Cluster name
        """

        self.name = name
        self._hosts = []
        self._dc = []

    def add_host(self, host=None, **kwargs):
        """ Adds zookeeper's server to cluster

        If given host is an object of Host than simply adds to cluster
        otherwise creates one from kwargs.

        Args:
            host: Instance of Host class
            **kwargs: See Host's constructor
        Raises:
            ClusterHostAddError: If cannot add host with given params
            ClusterHostCreateError: If cannot create host with given params
            ClusterHostDuplicateError: If cannot add host because the same exists
        """
        if host is None:
            try:
                host = Host(**kwargs)
            except Exception as exception:
                raise ClusterHostCreateError(
                    'Unable to create host: {} {} - {}'.format(host, kwargs, exception))

        if isinstance(host, Host):
            if self.host_is_duplicated(host):
                raise ClusterHostDuplicateError('Unable to add duplicated host: {}'.format(host))
            host.cluster = self.name
            self._hosts.append(host)
            if host.dc:
                self.add_dc(host.dc)
        else:
            raise ClusterHostAddError('Unable to add host: {} {}:'.format(host, kwargs))

    def host_is_duplicated(self, host):
        """ Checks if host exists in the cluster

        Matching is based on two vars ip and port

        Args:
            host: host object
        Returns:
            True or False :)
        """
        for item in self.get_hosts():
            if str(host) == str(item):
                return True
        return False

    def add_dc(self, name):
        """ Adds DC to known dc list

        Args:
            name: DC's name
        Returns:
            If item existed in the dc list returns False, otherwise True
        """
        if name not in self._dc:
            self._dc.append(name)
            return True
        return False

    def get_hosts(self):
        """ Gets all hosts

        Returns:
            List of host's object
        """
        return self._hosts

    def get_host(self, name):
        """ Gets host by given name

        Args:
            name: Host's name
        Returns:
            Host object
        Raises:
            ClusterHostDoesNotExistsError: If host has not been found in the cluster
        """
        name = name.lower().strip()
        for host in self.get_hosts():
            if str(host) == name:
                return host
        return None

    def __str__(self):
        return self.name
