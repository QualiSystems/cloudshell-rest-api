# cloudshell-rest-api

[![Build status](https://github.com/QualiSystems/cloudshell-rest-api/workflows/CI/badge.svg?branch=master)](https://github.com/QualiSystems/cloudshell-rest-api/actions?query=branch%3Amaster)
[![codecov](https://codecov.io/gh/QualiSystems/cloudshell-rest-api/branch/master/graph/badge.svg)](https://codecov.io/gh/QualiSystems/cloudshell-rest-api)
[![PyPI version](https://badge.fury.io/py/cloudshell-rest-api.svg)](https://badge.fury.io/py/cloudshell-rest-api)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

## Features

* Add Shell - adds a new Shell Entity (supported from CloudShell 8.0)
* Update Shell - updates an existing Shell Entity (supported from CloudShell 8.0)
* Delete Shell - removes an existing Shell Entity (supported from CloudShell 9.2)
* Get Shell - get Shell's information
* Get Installed Standards - gets a list of standards and matching versions installed on CloudShell (supported from CloudShell 8.1)
* Import Package - imports a package to CloudShell
* Export Package - exports a package from CloudShell


## Installation

```bash
pip install cloudshell-rest-api
```

## Getting started

```python
from cloudshell.rest.api import PackagingRestApiClient
# Loging to CloudShell
client = PackagingRestApiClient.login("HOST", "USERNAME", "PASSWORD", "DOMAIN")
# Or connect with a token
client = PackagingRestApiClient("HOST", "TOKEN")
# Add a new Shell to CloudShell
client.add_shell("SHELL_PATH.zip")
```

## License

* Free software: Apache Software License 2.0
