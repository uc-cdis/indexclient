from setuptools import setup

setup(
    name='indexclient',
    version='2.0.0',
    packages=[
        'indexclient',
        'indexclient.parsers',
    ],
    install_requires=[
        'requests>=2.5.2,<3.0.0',
    ],
)
