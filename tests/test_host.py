# -*- coding:utf-8 -*-
import socket
import sys
import time
from functools import partial
from tornado import gen
from tornado.testing import AsyncTestCase, gen_test
from zookeeper_monitor import zk
from .fixtures import host as FIXTURE


try:
    from unittest.mock import call, patch, Mock, MagicMock
except:
    from mock import call, patch, Mock, MagicMock


class HostTest(AsyncTestCase):

    def setUp(self):
        super(HostTest, self).setUp()
        self.maxDiff = None

    def tearDown(self):
        patch.stopall()
        super(HostTest, self).tearDown()

    def test_parse_info_ok(self):
        for case in FIXTURE.parse_info_data['ok']:
            host = zk.Host('localhost', 2181)
            ret = host._parse_info(case['in'])
            for attr, val in case['out'].items():
                self.assertEqual(host.info[attr], val)
                self.assertEqual(ret[attr], val)
            self.assertEqual(getattr(host, 'health'), getattr(zk.Host, case['health']))
            self.assertEqual(host.info['mode'], getattr(zk.Host, case['mode'], case['mode']))

    def test_parse_info_ok_wo_update(self):
        for case in FIXTURE.parse_info_data['ok']:
            host = zk.Host('localhost', 2181)
            ret = host._parse_info(case['in'], update_host_info=False)
            for attr, val in case['out'].items():
                self.assertFalse(attr in host.info and host.info[attr])
                self.assertEqual(ret[attr], val)
            self.assertEqual(getattr(host, 'health'), getattr(zk.Host, case['health']))
            self.assertEqual(host.info['mode'], zk.Host.UNKNOWN)

    def test_parse_info_err_parse(self):
        for case in FIXTURE.parse_info_data['raise_on_parse']:
            host = zk.Host('localhost', 2181)
            host.is_valid = MagicMock(return_value=True)

            self.assertRaises(zk.HostInvalidInfo, partial(host._parse_info, case['in']))
            self.assertEqual(getattr(host, 'health'), getattr(zk.Host, case['health']))

            host.is_valid.assert_called_once()
            self.assertEqual(host.info['mode'], getattr(zk.Host, case['mode'], case['mode']))

    def test_parse_info_err_validate(self):
        for case in FIXTURE.parse_info_data['raise_on_validate']:
            host = zk.Host('localhost', 2181)

            self.assertRaises(zk.HostInvalidInfo, partial(host._parse_info, case['in']))
            self.assertEqual(getattr(host, 'health'), getattr(zk.Host, case['health']))

            self.assertEqual(host.info['mode'], getattr(zk.Host, case['mode'], case['mode']))

    def test_parse_stat(self):
        for name, case in FIXTURE.parse_stat_data.items():
            host = zk.Host('localhost', 2181)
            print('CASE %s', name)
            parsed, not_parsed, errors = host._parse_stat(case['in'])
            self.assertEqual(parsed, case['parsed'])
            self.assertEqual(not_parsed, case['not_parsed'])

    def test_parse_stat_error(self):
        re_obj = MagicMock()
        match_obj = Mock()
        re_obj.search = MagicMock(return_value=match_obj)
        patch('zookeeper_monitor.zk.host.re', re_obj).start()

        keyerror = MagicMock(return_value={'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 6})
        too_few = MagicMock(return_value=[1,2,3,4])
        too_many = MagicMock(return_value=[1,2,3,4,5,6,7])

        case = FIXTURE.parse_stat_data['ok']
        for groups_mock in [keyerror, too_few, too_many]:

            match_obj.groups = groups_mock
            host = zk.Host('localhost', 2181)
            parsed, not_parsed, errors = host._parse_stat(case['in'])

            self.assertNotEqual(parsed, case['parsed'])
            self.assertEqual(not_parsed, [])

            proper = dict(case['parsed'])
            proper['clients'] = []

            self.assertEqual(parsed, proper)
            self.assertEqual(
                errors, [el.strip() for el in case['in'] if not el.startswith('Zookeeper')])

    def test_init_default(self):
        host = zk.Host('localhost')
        self.assertEqual(host.addr, 'localhost')
        self.assertEqual(host.port, 2181)
        self.assertEqual(host.dc, None)
        self.assertEqual(host.cluster, None)
        self.assertIsInstance(host.timeout, int)
        self.assertEqual(host.info['zxid'], None)
        self.assertEqual(host.info['mode'], zk.Host.UNKNOWN)
        self.assertEqual(host.health, zk.Host.HOST_UNCHECKED)

    def test_init(self):
        host = zk.Host('dummy', port=9999, cluster='FAKE', dc='eu-west', timeout=888)
        self.assertEqual(host.addr, 'dummy')
        self.assertEqual(host.port, 9999)
        self.assertEqual(host.dc, 'eu-west')
        self.assertEqual(host.cluster, 'FAKE')
        self.assertEqual(host.timeout, 888)
        self.assertEqual(host.info['zxid'], None)
        self.assertEqual(host.info['mode'], zk.Host.UNKNOWN)
        self.assertEqual(host.health, zk.Host.HOST_UNCHECKED)

    def test_init_err_no_addr(self):
        self.assertRaises(TypeError, partial(zk.Host, port=9999, dc='eu-west'))

    def _prepare_executes_mock(self, ip='127.0.0.1', **kwargs):
        iostream_obj = MagicMock()
        for attr, val in kwargs.items():
            mock = val if (isinstance(val, Mock) or hasattr(val, '__call__')) else MagicMock(return_value=val)
            setattr(iostream_obj, attr, mock)
        iostream = MagicMock(return_value=iostream_obj)

        resolver = MagicMock(
            return_value=gen.maybe_future((socket.AF_INET, ip))
        )
        patch('zookeeper_monitor.zk.host.Host._resolve', resolver).start()
        patch('zookeeper_monitor.zk.host.socket.socket', MagicMock).start()
        patch('zookeeper_monitor.zk.host.IOStream', iostream).start()
        patch('zookeeper_monitor.zk.host.IOLoop', self.io_loop).start()

        return resolver, iostream, iostream_obj

    @gen_test
    def test_execute(self):
        some_data = 'DATA'
        some_ip = '123.45.67.89',

        resolver, iostream, iostream_obj = self._prepare_executes_mock(
            ip=some_ip,
            connect=None,
            write=gen.maybe_future(True),
            read_until_close=gen.maybe_future(some_data)
        )

        host = zk.Host('dummy.host', 2181)
        ret_test = yield host.execute('sample_command')

        self.assertEqual(ret_test, some_data)
        self.assertEqual(resolver.call_count, 1)
        iostream_obj.connect.assert_called_once_with(some_ip)
        iostream_obj.write.assert_called_once_with(b'sample_command\n')

        iostream_obj.write.reset_mock()
        yield host.execute('    B__sample_command                     \n')
        iostream_obj.write.assert_called_once_with(b'B__sample_command\n')

    @gen_test
    def test_execute_timeout(self):
        some_data = 'DATA'

        @gen.coroutine
        def fake_write(data):
            yield gen.Task(self.io_loop.add_timeout, time.time() + 0.2)

        resolver, iostream, iostream_obj = self._prepare_executes_mock(
            connect=None,
            close=None,
            write=fake_write,
            read_until_close=gen.maybe_future(some_data)
        )

        host = zk.Host('dummy.host', 2181)
        host.set_timeout(0.1)
        try:
            self.stop()
            yield host.execute('cmd')
            self.wait()
        except:
            ex_type = sys.exc_info()[0]
            self.assertEqual(ex_type, zk.host.HostConnectionTimeout)
        else:
            self.fail('Timeout didn\'t work')

        iostream_obj.close.assert_called_once_with(True)

    def test_set_timeout(self):
        host = zk.Host('localhost', 2181)
        host.set_timeout(100)
        self.assertEqual(host.timeout, 100)
        host.set_timeout(0.01)
        self.assertEqual(host.timeout, 0.01)
        self.assertRaises(zk.HostSetTimeoutValueError, partial(host.set_timeout, -1))
        self.assertRaises(zk.HostSetTimeoutTypeError, partial(host.set_timeout, 'string'))

    def test_str(self):
        host = zk.Host('dummy.host.domain', 1133)
        self.assertEqual(str(host), 'dummy.host.domain:1133')

    def test_repr(self):
        host = zk.Host('dummy.host.domain', 1133)
        self.assertIn('dummy.host.domain:1133', repr(host))

    @gen_test
    def test_get_info(self):
        host = zk.Host('localhost', 2181)
        host.srvr = MagicMock(return_value=gen.maybe_future('Some result'))
        res = yield host.get_info()
        host.srvr.assert_called_once()
        self.assertIsInstance(res, dict)

    @gen_test
    def test_resolve(self):
        ph_io_loop = 'ioloop placeholder'
        resolver_obj = Mock()
        resolver_obj.resolve = MagicMock(return_value=gen.maybe_future(('a', 'b', 'c')))
        resolver = MagicMock(return_value=resolver_obj)
        patch('zookeeper_monitor.zk.host.Resolver', resolver).start()
        host = zk.Host('localhost', 2181)
        res = yield host._resolve(ph_io_loop)
        resolver.assert_called_once_with(io_loop=ph_io_loop)
        resolver_obj.assert_called_once()
        self.assertEqual(res, 'a')

    @gen_test
    def test_srvr_ok(self):
        host = zk.Host('localhost', 2181)
        host.execute = MagicMock(return_value=gen.maybe_future(
            FIXTURE.result_of_execute_srvr_ok.encode('utf-8')
        ))
        ret = yield host.srvr()
        host.execute.assert_called_once_with('srvr')
        self.assertEqual(host.health, zk.Host.HOST_HEALTHY)
        self.assertIsInstance(ret, dict)

    @gen_test
    def test_srvr_err(self):
        host = zk.Host('localhost', 2181)
        host.execute = MagicMock(return_value=gen.maybe_future(
            FIXTURE.result_of_execute_srvr_err.encode('utf-8')
        ))
        ret = yield host.srvr()
        host.execute.assert_called_once()
        self.assertEqual(host.health, zk.Host.HOST_ERROR)
        self.assertFalse(ret)

        host = zk.Host('localhost', 2181)
        host.execute = MagicMock(side_effect=Exception)
        ret = yield host.srvr()
        self.assertFalse(ret)
        self.assertEqual(host.health, zk.Host.HOST_ERROR)

    @gen_test
    def test_srvr_timeout(self):
        host = zk.Host('localhost', 2181)
        host.execute = MagicMock(side_effect=zk.host.HostConnectionTimeout)
        ret = yield host.srvr()
        self.assertFalse(ret)
        self.assertEqual(host.health, zk.Host.HOST_TIMEOUT)

    @gen_test
    def test_envi(self):
        host = zk.Host('localhost', 2181)
        host.execute = MagicMock(return_value=gen.maybe_future(
            FIXTURE.envi['in'].encode('utf-8')
        ))
        ret = yield host.envi()
        host.execute.assert_called_once_with('envi')
        self.assertEqual(ret, FIXTURE.envi['out'])

    @gen_test
    def test_dump_kill_srst_ruok_reqs(self):
        for cmd in ['dump', 'kill', 'ruok', 'srst', 'reqs']:
            host = zk.Host('localhost', 2181)
            host.execute = MagicMock(return_value=gen.maybe_future(
                FIXTURE.simple['in'].encode('utf-8')
            ))
            method = getattr(host, cmd)
            ret = yield method()
            host.execute.assert_called_once_with(cmd)
            host.execute.reset_mock()
            self.assertEqual(ret.decode('utf-8'), FIXTURE.simple['out'])

