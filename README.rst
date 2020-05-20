===================
cloudshell-rest-api
===================

.. image:: https://travis-ci.org/QualiSystems/cloudshell-rest-api.svg?branch=master
    :target: https://travis-ci.org/QualiSystems/cloudshell-rest-api

.. image:: https://codecov.io/gh/QualiSystems/cloudshell-rest-api/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/QualiSystems/cloudshell-rest-api

.. image:: https://img.shields.io/pypi/v/cloudshell-rest-api.svg?maxAge=2592000
    :target: https://img.shields.io/pypi/v/cloudshell-rest-api.svg?maxAge=2592000

Python client for the CloudShell REST API


Features
--------

* Add Shell - adds a new Shell Entity (supported from CloudShell 7.2)
* Update Shell - updates an existing Shell Entity (supported from CloudShell 7.2)
* Delete Shell - removes an existing Shell Entity (supported from CloudShell 9.2)
* Get Shell - get Shell's information
* Get Installed Standards - gets a list of standards and matching versions installed on CloudShell (supported from CloudShell 8.1)
* Import Package - imports a package to CloudShell
* Export Package - exports a package from CloudShell

Installation
------------

Install cloudshell-rest-api Python package from PyPI::

    pip install cloudshell-rest-api


Install with dependencies for async API client::

    pip install cloudshell-resp-api[async]


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


