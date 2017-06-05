===================
cloudshell-rest-api
===================

.. image:: https://travis-ci.org/QualiSystems/cloudshell-rest-api.svg?branch=master
    :target: https://travis-ci.org/QualiSystems/cloudshell-rest-api

.. image:: https://coveralls.io/repos/github/QualiSystems/cloudshell-rest-api/badge.svg?branch=master
    :target: https://coveralls.io/github/QualiSystems/cloudshell-rest-api?branch=master

.. image:: https://img.shields.io/pypi/v/cloudshell-rest-api.svg?maxAge=2592000
    :target: https://img.shields.io/pypi/v/cloudshell-rest-api.svg?maxAge=2592000

Python client for the CloudShell REST API


Features
--------

* Add Shell - adds a new Shell Entity (supported from CloudShell 7.2)
* Update Shell - updates an existing Shell Entity (supported from CloudShell 7.2)
* Get Installed Standards - gets a list of standards and matching versions installed on CloudShell (supported from CloudShell 8.1)

Installation
------------

Install cloudshell-rest-api Python package from PyPI::

    pip install cloudshell-rest-api


Getting started
---------------

Make sure to include this line in the beginning of your file::

    from cloudshell.rest.api import PackagingRestApiClient


Login to CloudShell::

    client = PackagingRestApiClient('SERVER', 9000, 'USER', 'PASS', 'Global')


Add a new Shell to CloudShell::

    client.add_shell('work//NutShell.zip')



License
-------

* Free software: Apache Software License 2.0


