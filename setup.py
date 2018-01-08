from setuptools import setup

setup(
    name='indexclient',
    version='0.1',
    packages=[
        'indexclient',
        'indexclient.parsers',
    ],
    install_requires=[
        'requests>=2.5.2',
    ],
)
