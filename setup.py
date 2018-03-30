from setuptools import setup

setup(
    name='indexclient',
    version='1.4.3',
    packages=[
        'indexclient',
        'indexclient.parsers',
    ],
    install_requires=[
        'requests>=2.5.2,<3.0.0',
    ],
)
