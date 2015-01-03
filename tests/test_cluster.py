# -*- coding:utf-8 -*-
import socket
import sys
import time
from functools import partial
from tornado import gen
from tornado.testing import AsyncTestCase, gen_test
from zookeeper_monitor import zk


try:
    from unittest.mock import patch, Mock, MagicMock
except:
    from mock import patch, Mock, MagicMock


class ClusterTest(AsyncTestCase):

    FIXTURE_NAME = 'SomeClusterName'
    FIXTURE_HOST = 'dummyhost.ip'
    FIXTURE_HOST_2 = 'secondhost.ip'
    FIXTURE_PORT = 2818

    def setUp(self):
        super(ClusterTest, self).setUp()
        self.maxDiff = None
        self.cluster = zk.Cluster(self.FIXTURE_NAME)

    def tearDown(self):
        patch.stopall()
        super(ClusterTest, self).tearDown()

    def test_init(self):
        self.assertEqual(self.cluster.name, self.FIXTURE_NAME)
        self.assertEqual(self.cluster._hosts, [])
        self.assertEqual(self.cluster._dc, [])

    def test_add_host_no_host(self):
        self.assertRaises(zk.ClusterHostAddError, partial(self.cluster.add_host, host='FAIL'))
        self.assertRaises(zk.ClusterHostCreateError, self.cluster.add_host)

    def test_add_host_and_create(self):
        self.cluster.add_host(addr=self.FIXTURE_HOST, port=self.FIXTURE_PORT)
        self.assertEqual(len(self.cluster._hosts), 1)
        self.assertIsInstance(self.cluster._hosts[0], zk.Host)
        self.assertEqual(self.cluster._hosts[0].port, self.FIXTURE_PORT)
        self.assertEqual(self.cluster._hosts[0].addr, self.FIXTURE_HOST)
        self.assertEqual(self.cluster._hosts[0].cluster, str(self.cluster))

    def test_add_host_duplicated_host(self):
        self.cluster.add_host(addr=self.FIXTURE_HOST)
        self.assertRaises(zk.ClusterHostDuplicateError, partial(self.cluster.add_host, addr=self.FIXTURE_HOST))

    def test_add_host_object(self):
        host = zk.Host(self.FIXTURE_HOST, port=self.FIXTURE_PORT)
        self.cluster.add_host(host)
        self.assertEqual(len(self.cluster._hosts), 1)
        self.assertIsInstance(self.cluster._hosts[0], zk.Host)
        self.assertEqual(self.cluster._hosts[0].port, self.FIXTURE_PORT)
        self.assertEqual(self.cluster._hosts[0].addr, self.FIXTURE_HOST)
        self.assertEqual(self.cluster._hosts[0].cluster, str(self.cluster))

    def test_add_host_with_dc(self):
        self.cluster.add_dc = MagicMock()
        self.cluster.add_host(addr=self.FIXTURE_HOST, dc='eu-west')
        self.cluster.add_host(addr=self.FIXTURE_HOST_2, dc='sasd')
        self.cluster.add_host(addr='localhost')
        self.assertEqual(len(self.cluster._hosts), 3)
        self.assertEqual(self.cluster.add_dc.call_count, 2)

    def tet_host_is_duplicated(self):
        self.cluster._host = ['AAA', 'BBB', 'CCC']
        ret = self.cluster.host_is_duplicated('AAA')
        self.assertTrue(ret)
        ret = self.cluster.host_is_duplicated('AAa')
        self.assertFalse(ret)
        ret = self.cluster.host_is_duplicated('123')
        self.assertFalse(ret)

    def test_add_dc(self):
        ret = self.cluster.add_dc('a1')
        self.assertIn('a1', self.cluster._dc)
        self.assertTrue(ret)
        ret = self.cluster.add_dc('a1')
        self.assertEqual(len(self.cluster._dc), 1)
        self.assertFalse(ret)
        ret = self.cluster.add_dc('A1')
        self.assertIn('A1', self.cluster._dc)
        self.assertTrue(ret)

    def test_get_host(self):
        self.cluster.get_hosts = MagicMock(return_value=['aaa', 'bbb', 'ccc'])
        ret = self.cluster.get_host('bbb')
        self.assertEqual(ret, 'bbb')
        ret = self.cluster.get_host('AAa')
        self.assertEqual(ret, 'aaa')
        ret = self.cluster.get_host('   aaa   ')
        self.assertEqual(ret, 'aaa')
        ret = self.cluster.get_host('FFF')
        self.assertIsNone(ret)

    def test_str(self):
        self.assertEqual(str(self.cluster), self.FIXTURE_NAME)
