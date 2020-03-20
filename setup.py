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
<<<<<<< HEAD
    description='Python module for couchdb')
=======
    description='Python module for couchdb',
    scripts=['tools/dumpdb.py', 'tools/restoredb.py'],
)
>>>>>>> 585a0a8017c9a2f80cb6ecc95ca534124adb6e5b
