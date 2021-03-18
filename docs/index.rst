Welcome to PyCouchDB's documentation!
=====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

PyCouchDB Client
================
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

.. automodule:: pycouchdb.client
.. autoclass:: Client
   :members:

PyCouchDB Database
==================
.. automodule:: pycouchdb.db
.. autoclass:: Database
   :members:

PyCouchDB Server
================
.. automodule:: pycouchdb.server
.. autoclass:: Server
      :members: