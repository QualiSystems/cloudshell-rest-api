#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import setup, find_packages


def get_file_content(file_name):
    with open(file_name) as f:
        return f.read()

readme = get_file_content('README.rst')

history = get_file_content('HISTORY.rst')

exec(open('cloudshell/version.py').read())

setup(
    name='cloudshell-rest-api',
    version=__version__,
    description="Python client for the CloudShell REST API",
    long_description=readme + '\n\n' + history,
    author="Boris Modylevsky",
    author_email='borismod@gmail.com',
    url='https://github.com/borismod/cloudshell_rest_api',
    packages=find_packages(),
    include_package_data=True,
    install_requires=get_file_content('requirements.txt'),
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='cloudshell quali sandbox cloud rest api',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=get_file_content('test_requirements.txt')
)
