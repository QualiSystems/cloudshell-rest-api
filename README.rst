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
* Update Shell - adds a new Shell Entity (supported from CloudShell 7.2)

Installation
------------

Install cloudshell-rest-api Python package from PyPI::

    pip install cloudshell-rest-api


Getting started
---------------

Make sure to include this line in the beginning of your file::

    from cloudshell_rest_api.cloudshell.rest.api import CloudShellRestApiClient


Login to CloudShell::

    client = CloudShellRestApiClient('SERVER', 9000, 'USER', 'PASS', 'Global')


Add a new Shell to CloudShell::

    client.add_shell('work//NutShell.zip')



License
-------

* Free software: Apache Software License 2.0


