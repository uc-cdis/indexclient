from setuptools import setup

setup(
    name="indexclient",
    version="1.6.2",
    packages=["indexclient", "indexclient.parsers"],
    install_requires=["requests>=2.5.2,<3.0.0"],
)
