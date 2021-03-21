from setuptools import setup
from pycouchdb import __version__

name = 'pycouchdb'
version:str = __version__

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name=name,
    version=version,
    packages=['pycouchdb', 'pycouchdb/connections'],
    url='https://github.com/angrysoft/pycouchdb',
    license='Apache 2.0',
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    author='AngrySoft Sebastian Zwierzchowski',
    author_email='sebastian.zwierzchowski@gmail.com',
    description='Python module for couchdb',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    scripts=['pycouchctl.py',],
)
