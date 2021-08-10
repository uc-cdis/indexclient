from setuptools import find_packages, setup

setup(
    name='indexclient',
    version='2.0.0',
    packages=find_packages(),
    install_requires=[
        'requests~=2.5',
    ],
)
