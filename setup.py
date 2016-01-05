#!/usr/bin/env python
# -*- coding:utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

exec(open('zookeeper_monitor/version.py', 'r').read())

setup(
    name='zookeeper_monitor',
    packages=['zookeeper_monitor', 'zookeeper_monitor.zk'],
    version=__version__,
    author='Krzysztof Warunek',
    author_email='krzysztof@warunek.net',
    description='Zookeeper\'s four letters command wrapper and web monitor.',
    include_package_data = True,
    keywords='zookeeper, tcp, tornado',
    url='https://github.com/kwarunek/zookeeper_monitor',
    long_description=open('README.rst').read(),
    install_requires=open('requirements.txt', 'r').read(),
    tests_require=['mock', 'nose', 'coverage'],
    license="MIT",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Operating System :: POSIX',
        'Development Status :: 4 - Beta'
    ]
)
