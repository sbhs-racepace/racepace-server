import os
from setuptools import setup, find_packages

setup(
    name='server',
    packages=['server', 'server.core'],
    version='1.0.1',
    python_requires='>=3.7',
)
