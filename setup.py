#!/usr/bin/env python

from setuptools import setup

setup(
    name="nfq-xfp",
    description="Xdr based Files Parser",
    version="0.0.0a0",
    author="Hugo Marrao",
    author_email="hugo.marrao@nfq.es",
    packages=[
        'nfq',
        'nfq.xfp'
        ],
    zip_safe=False,
    install_requires=[],
    include_package_data=True,
    setup_requires=['pytest-runner', 'pytest'],
    tests_require=['pytest']
    )
