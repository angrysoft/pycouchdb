PyCouchdb
=========

Python library for `CouchDb`_


- Library `documentation`_
- pypi `Downloads`_

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

.. _Downloads: http://pypi.python.org/pypi/PyCouchDB
.. _PyPI: http://pypi.python.org/
.. _documentation: http://pycouchdb.readthedocs.io/en/latest/
.. _CouchDb: https://couchdb.apache.org/