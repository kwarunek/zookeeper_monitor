zookeeper_monitor
==================

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


Web monitor
-----------

To run web monitor you need to provide configuration, if you don't it will used as default `localhost:2181`.
    
.. code-block:: bash

    python -m zookeeper_monitor.web


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
    
- name (string): cluster name
- hosts (list): List of hosts running ZooKeeper connected in cluster
    
    Host object:
        - addr (string): IP or domain, mandatory
        - port (int): ZooKeeper port, optional, default 2181
        - dc (string): datacenter/location name, optional

License
-------
MIT

TODO
----
- more tests
- more stats in webmonitor


Changelog
---------

0.1.2 - **release** - pypi
0.1.1 - clean up
0.1.0 - public standalone
0.0.3 - 0.0.9 - refactor, tests
0.0.2 - working draft
0.0.1 - initial concept
