from setuptools import setup

setup(
    name='index',
    version='0.1',
    packages=[
        'index',
        'index.parsers',
    ],
    install_requires=[
        'requests==2.7.0',
    ],
)
