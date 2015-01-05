zookeeper_monitor
==================

|image0|_ |image2|_ |image1|_

.. |image0| image:: https://api.travis-ci.org/kAlmAcetA/zookeeper_monitor.png?branch=master
.. _image0: https://travis-ci.org/kAlmAcetA/zookeeper_monitor
.. |image1| image:: https://landscape.io/github/kAlmAcetA/zookeeper_monitor/master/landscape.svg?style=flat
.. _image1: https://landscape.io/github/kAlmAcetA/zookeeper_monitor
.. |image2| image:: https://pypip.in/version/zookeeper_monitor/badge.svg?style=flat
.. _image2: https://pypi.python.org/pypi/zookeeper_monitor

Module lets you call ZooKeeper commands - four letters commands over TCP - https://zookeeper.apache.org/doc/r3.1.2/zookeeperAdmin.html#sc_zkCommands. It also has built-in web monitor. Based on Tornado, compatibile with Python 2.7.x, 3.x and above. It doesn't require zookeeper, nor zookeeper's headers (since it doesn't utilize zkpython).

Installation
------------

It can be installed from pypi or directly from git repository.

.. code-block:: bash

    pip install zookeeper_monitor

    #or

    git clone https://github.com/kAlmAcetA/zookeeper_monitor.git
    cd zookeeper_monitor/
    python setup.py install

Usage
------------

Example:

.. code-block:: python

    from zookeeper_monitor import zk

    @tornado.gen.coroutine
    def some_coroutine()
        host = zk.Host('zookeeper.addr.ip', 2181)
        # you can run each command as a coroutine example:
        # get srvr data
        srvr_data = yield host.srvr()
        # get stat data
        stat_data = yield host.stat()
        # get server state
        ruok = yield host.ruok()
        # stop zookeeper
        yield host.kill()


You can wrap it to sync code if you are not using tornado

.. code-block:: python

    from tornado.ioloop import IOLoop

    IOLoop.instance().run_sync(some_coroutine)


Web monitor
-----------

To run web monitor you need to provide configuration, if you don't, it will used `localhost:2181` by default.

.. code-block:: bash

    python -m zookeeper_monitor.web

    # with configuration file
    python -m zookeeper_monitor.web -c /somepath/cluster.json

    # to see available options
    python -m zookeeper_monitor.web --help


Next you navigate to http://127.0.0.1:8080/ (or whatever you specified).

Configuration
-------------

Defining cluster `cluster.json` (json or yaml)

.. code-block:: json

    {
        "name": "brand-new-zookeeper-cluster",
        "hosts": [
            {"addr": "10.1.15.1", "port": 2181, "dc":"eu-west"},
            {"addr": "10.2.31.2", "port": 2181, "dc":"us-east"},
            {"addr": "10.1.12.3", "port": 2181, "dc":"eu-west"}
        ]
    }


* name (string) - cluster name.
* hosts (list) - List of hosts running ZooKeeper connected in cluster:

  - addr (string): IP or domain, mandatory
  - port (int): ZooKeeper port, optional, default 2181
  - dc (string): datacenter/location name, optional
  
Screenshots
-----------

Cluster view
|image22|_

.. |image22| image:: https://cloud.githubusercontent.com/assets/670887/5609840/172c1e38-94aa-11e4-92e5-9b4e8a06632c.png
.. _image22: https://cloud.githubusercontent.com/assets/670887/5609840/172c1e38-94aa-11e4-92e5-9b4e8a06632c.png

Node stat view
|image23|_

.. |image23| image:: https://cloud.githubusercontent.com/assets/670887/5609842/1be19584-94aa-11e4-8cd1-5df63c1bfaaf.png
.. _image23: https://cloud.githubusercontent.com/assets/670887/5609842/1be19584-94aa-11e4-8cd1-5df63c1bfaaf.png

License
-------
MIT

TODO
----
- more tests
- more stats in webmonitor
- parse zookeeper version
- new commands in zookeeper 3.3 and 3.4
- parse output of dump, reqs

Changelog
---------

0.2.2 - clean ups: pylint, README, classifiers

0.2.1 - fix package, fix tests

0.2.0 - implement more commands, updated docs

0.1.2 - **release** - pypi

0.1.1 - clean up

0.1.0 - public standalone

0.0.3 - 0.0.9 - refactor, tests

0.0.2 - working draft

0.0.1 - initial concept
