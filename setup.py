from setuptools import setup
from .pycouchdb import __version__

name = 'pycouchdb'
version:str = __version__

setup(
    name=name,
    version=version,
    packages=['pycouchdb'],
    url='https://github.com/angrysoft/pycouchdb',
    license='Apache 2.0',
    author='AngrySoft Sebastian Zwierzchowski',
    author_email='sebastian.zwierzchowski@gmail.com',
    description='Python module for couchdb',
    scripts=['tools/pycouchctl.py',],
)
