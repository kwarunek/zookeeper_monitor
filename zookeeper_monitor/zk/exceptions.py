# -*- coding:utf-8 -*-
""" Exceptions used in this module.

Couple of them are covering raised TypeError, ValueError, KeyError.
If you want to catch all of them simply except ZkBaseError.

"""


class ZkBaseError(Exception):
    """ Base zookeeper_monitor zk-related exception """
    pass


class ClusterBaseError(ZkBaseError):
    """ Base zookeeper_monitor cluster exception """
    pass


class ClusterHostAddError(ClusterBaseError):
    """ Trying to add host to the cluster """
    pass


class ClusterHostCreateError(ClusterBaseError):
    """ Trying create Host object based on params """
    pass


class ClusterHostDuplicateError(ClusterHostAddError):
    """ Trying add host to the cluster with the same IP and port """
    pass


class ClusterHostDoesNotExistsError(ClusterBaseError):
    """ Get host by name that doen't exist """
    pass


class HostBaseError(ZkBaseError):
    """ Base zookeeper_monitor host exception """
    pass


class HostInvalidInfo(HostBaseError):
    """ Trying to update host info with invalid data """
    pass


class HostConnectionTimeout(HostBaseError):
    """ Command to zookeeper timeouted """
    pass


class HostSetTimeoutTypeError(TypeError, HostBaseError):
    """ Trying to set timeout that is not int or float """
    pass


class HostSetTimeoutValueError(ValueError, HostBaseError):
    """ Trying to set timeout that below 0 """
    pass
