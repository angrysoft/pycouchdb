from setuptools import setup

name = 'pycouchdb'
version = '0.2'

setup(
    name=name,
    version=version,
    packages=['pycouchdb'],
    url='',
    license='Apache 2.0',
    author='AngrySoft',
    author_email='sebastian.zwierzchowski@gmail.com',
    description='Python module for couchdb',
    scripts=['tools/dumpdb.py', 'tools/restoredb.py'],
)
