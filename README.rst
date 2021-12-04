PyCouchdb
=========

Python client library for `CouchDb`_  3.x.x


- Library `documentation`_
- pypi

Example
-------
.. code-block:: python
   
   >>> from pycouchdb import Client
   >>> cli = Client('http://admin:admin@localhost')

Create database and get access , update

.. code-block:: python
   
   >>> cli.create('userdb')
   >>> users = cli.get_db('userdb')
   >>> usr = {'name': 'john', 'lastname':'doe'}
   >>> _id, _rev = users.add(usr)
   >>> updated_usr = {'name': 'john', 'lastname':'doe', 'email': 'john.doe@localhost'}
   >>> _id, _rev = users.update(_id, updated_usr)
   >>> users.delete(_id)
   >>> cli.delete('usersdb')

.. _Downloads: http://pypi.python.org/pypi/python-pycouchdb
.. _documentation: https://python-pycouchdb.readthedocs.io/en/latest/
.. _CouchDb: https://couchdb.apache.org/
