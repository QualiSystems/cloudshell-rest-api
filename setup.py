#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.version import StrictVersion

from setuptools import find_packages, setup
from setuptools.version import __version__ as setuptools_version


if StrictVersion(setuptools_version) < StrictVersion("40.0"):
    import os
    import sys

    python = sys.executable
    try:
        s = os.system('{} -m pip install "setuptools>=40"'.format(python))
        if s != 0:
            raise Exception
    except Exception:
        raise Exception(
            "Failed to update setuptools. Setuptools>40 have to be installed"
        )
    # reran setup.py
    os.execl(python, python, *sys.argv)


def get_file_content(file_name):
    with open(file_name) as f:
        return f.read()


readme = get_file_content("README.rst")
history = get_file_content("HISTORY.rst")
version = get_file_content("version.txt")

setup(
    name="cloudshell-rest-api",
    version=version,
    description="Python client for the CloudShell REST API",
    long_description=readme + "\n\n" + history,
    author="Boris Modylevsky",
    author_email="borismod@gmail.com",
    url="https://github.com/borismod/cloudshell_rest_api",
    packages=find_packages(),
    include_package_data=True,
    install_requires=get_file_content("requirements.txt"),
    extras_require={
        "async": [
            "aiohttp>=3.6.2,<3.7",
            "aiofiles>=0.4,<0.5",
            "async-property>=0.2.1,<0.3",
        ],
    },
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords="cloudshell quali sandbox cloud rest api",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    test_suite="tests",
    tests_require=get_file_content("test_requirements.txt"),
    setup_requires=["setuptools>=40"],
)
