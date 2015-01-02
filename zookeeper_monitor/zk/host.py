# -*- coding:utf-8 -*-
""" Host object represents zookeeper server.

Example:

    host = Host('localhost', 5555)
    result = yield host.stat()

"""
import functools
import re
import socket
import time
import logging
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.iostream import IOStream
from tornado.netutil import Resolver
from .exceptions import HostConnectionTimeout, HostSetTimeoutTypeError
from .exceptions import HostSetTimeoutValueError, HostInvalidInfo


def command_executor(func):
    """ Command executor

    Prepare wrapper.
    """
    @gen.coroutine
    @functools.wraps(func)
    def wrapper(self, *args, **kwds):
        """ Wrapper

        Wraps exception handling, returns ret, updates host's health state

        """
        try:
            ret = yield func(self, *args, **kwds)
            raise gen.Return(ret)
        except gen.Return:
            raise
        except HostConnectionTimeout as exception:
            logging.warning('Exception: %s', exception)
            self.health = Host.HOST_TIMEOUT
        except Exception as exception:
            logging.warning('Exception: %s', exception)
            self.health = Host.HOST_ERROR
        raise gen.Return(False)

    return wrapper


class Host(object):
    """ Zookeeper's server """

    HOST_HEALTHY = 'OK'
    HOST_ERROR = 'ERROR'
    HOST_TIMEOUT = 'TIMEOUT'
    HOST_DOWN = 'DOWN'
    HOST_UNCHECKED = 'UNCHECKED'

    FOLLOWER = 'FOLLOWER'
    LEADER = 'LEADER'
    UNKNOWN = 'UNKNOWN'

    RE_STAT_LINE = re.compile(r'/([\.0-9]{7,}):(\d+)\[(\d+)\]\(queued=(\d+),recved=(\d+),sent=(\d+)\)')

    def __init__(self, addr, port=2181, cluster=None, dc=None, timeout=2):
        """ Create cluster's host

        Args:
            host: IP or hostname of zookeeper instance
            port: Zookeeper's listening port
            cluster: Optionally cluster object
            dc: Specify in which datacenter/location in host the cluster
            timeout: Zookeepers commands timeout
        """
        self.addr = addr.lower()
        self.port = port
        self.dc = dc
        self.cluster = str(cluster) if cluster else None
        self.health = Host.HOST_UNCHECKED
        self.info = {}
        self.info['zxid'] = None
        self.info['connections'] = None
        self.info['mode'] = Host.UNKNOWN
        self.set_timeout(timeout)

    def set_timeout(self, timeout):
        """ Sets commands timeout

        Command timeout that includes: connection time and whole request time

        Args:
            timeout (int, float): value must be >= 0
        """
        if not isinstance(timeout, (int, float)):
            raise HostSetTimeoutTypeError('Timeout type should be int or float')
        if timeout < 0:
            raise HostSetTimeoutValueError('Timeout should be postitve number or zero')
        self.timeout = timeout

    def __str__(self):
        """ Short, enough, stringify """
        return '{}:{}'.format(self.addr, self.port)

    def __repr__(self):
        """ Better representaion """
        return 'Host Object ({}) {}'.format(str(self), self.__dict__)

    def _parse_info(self, lines, update_host_info=True):
        """ Parses response with host's basic info
        Args:
            update_host_info: If true updates host info (zxid, conns, ...) from stat
        Returns:
            Normalized, parsed data dict
        """
        result = {}
        try:
            for line in lines:
                tmp = line.split(':', 1)
                if not tmp[0] or not tmp[1]:
                    continue
                key = tmp[0].strip().split(' ')[0].strip().lower()
                val = tmp[1].strip()
                result[key] = val

            result['mode'] = result['mode'].upper()
        except Exception as exception:
            self.health = Host.HOST_ERROR
            logging.warning('Exception: %s', exception)
            raise HostInvalidInfo('Parse - dump info: {}'.format(result))

        if not self.is_valid(result):
            self.health = Host.HOST_ERROR
            raise HostInvalidInfo('Validate - dump info: {}'.format(result))
        else:
            self.health = Host.HOST_HEALTHY

        if update_host_info:
            self.info.update(result)
        return result

    def is_valid(self, data):
        """ Validates host's attributes and sets health status

        Args:
            Data to validate
        Returns:
            True if valid, otherwise False
        """
        # TODO it is just too simple
        if 'zxid' not in data or 'mode' not in data or \
                data['mode'] not in [Host.LEADER, Host.FOLLOWER]:
            return False
        else:
            return True

    def _parse_stat(self, lines):
        """ Parse result of stat command

        Args:
            lines (list): List of line to parse
        Returns:
            Tuple of:
                - parsed (dict) - parsed data
                - not_parsd (list) - not parsed lines
                - errors (list) - lines that raise error
        """
        not_parsed = []
        errors = []
        data = {"head": "", "clients": []}
        for line in lines:
            line = line.strip()
            if line.startswith('Zookeeper'):
                data['head'] = line
                continue
            match = re.search(self.RE_STAT_LINE, line)
            if match:
                try:
                    if len(match.groups(0)) != 6:
                        raise Exception('Client\'s data length mismatch')
                    client = {
                        'host': match.groups(0)[0],
                        'port': match.groups(0)[1],
                        'n': match.groups(0)[2],
                        'queued': match.groups(0)[3],
                        'recved': match.groups(0)[4],
                        'sent': match.groups(0)[5]
                    }
                except Exception as exception:
                    logging.warning('Exception: %s', exception)
                    logging.warning('Dump client match: %s', match.groups(0))
                    errors.append(line)
                else:
                    data['clients'].append(client)
            else:
                not_parsed.append(line)
        return data, not_parsed, errors

    @command_executor
    @gen.coroutine
    def srvr(self, update_host_info=True):
        """ Invokes `srvr` command against host

        Executes and fetchs host's srvr. Applies data to object.

        Args:
            update_host_info: If true updates host info (zxid, conns, ...) from stat
        Returns:
            False when fails, parsed info dict
        """
        data = yield self.execute('srvr')
        string = data.decode('utf-8')
        lines = string.split('\n')
        res = self._parse_info(lines, update_host_info)
        raise gen.Return(res)

    @command_executor
    @gen.coroutine
    def stat(self, update_host_info=True):
        """ Invokes `stat` command against host

        Args:
            update_host_info: If true updates host info (zxid, conns, ...) from stat
        Returns:
            False when fails, parsed info dict
        """
        data = yield self.execute('stat')
        lines = data.decode('utf-8').split('\n')
        parsed, not_parsed, errors = self._parse_stat(lines)
        logging.debug(errors)
        info = self._parse_info(not_parsed, update_host_info)
        info.update(parsed)
        raise gen.Return(info)

    @gen.coroutine
    def get_info(self):
        """ Get host info dict

        Returns:
            Host's attributtes as dictionary.
        """
        raise gen.Return(self.__dict__)

    @gen.coroutine
    def execute(self, cmd):
        """ Executes `cmd` on host and returns results

        Creates socket and tries to execute command against zookeeper. Socket
        is limited by quasi-Tornado's timeout. It doesn't check validity of response.

        Note:
            Timeout should be implemented using tornado.concurrent.chain_future:
            https://github.com/tornadoweb/tornado/blob/master/tornado/concurrent.py#L316

            such a wrapper exists in Tornado 4.0+ - with_timeout
            https://github.com/tornadoweb/tornado/blob/master/tornado/gen.py#L507

        Args:
            cmd: Four-letter string containing command to execute
        Returns:
            Raw response - bytes.
        Raises:
            HostConnectionTimeout: If sum times of connection, request, respons exceeds timeout
            Socket Errors: like ECONNNECTIONREFUSED,...
        """

        def on_timeout():
            """ Timeout handler

            Raises:
                HostConnectionTimeout: Raised to propagate error

            """
            stream.close(True)
            raise HostConnectionTimeout('Unable to connect to {} on {}'.format(self.addr, self.port))

        ioloop = IOLoop.current()
        address_family, addr = yield self._resolve(ioloop)
        stream = IOStream(socket.socket(address_family), io_loop=ioloop)

        # we need some timeout...
        timeout = ioloop.add_timeout(time.time() + self.timeout, on_timeout)

        stream.connect(addr)
        cmd = '{}\n'.format(cmd.strip())
        yield stream.write(cmd.encode('utf-8'))

        data = yield stream.read_until_close()
        ioloop.remove_timeout(timeout)

        raise gen.Return(data)

    @gen.coroutine
    def _resolve(self, ioloop):
        """ Resolve host addr (domain)

        Args:
            ioloop (IOLoop): io_loop to use
        Returns:
            Tuple of address family and ip address
        """
        resolver = Resolver(io_loop=ioloop)
        addrinfo = yield resolver.resolve(self.addr, int(self.port), socket.AF_UNSPEC)
        raise gen.Return(addrinfo[0])
