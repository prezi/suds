from setuptools import setup, find_packages

from prezi.setuputils.git import fetch_version

setup(
    name='prezi-suds',
    description="A lightweight soap-based client for python. This is a fork of the SUDS lib.",
    url='https://github.com/prezi/prezi-suds/',
    version=fetch_version(__file__),
    packages=find_packages(),
    include_package_data=True,
)
