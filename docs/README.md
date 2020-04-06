Welcome to PyCouchDB's documentation!
*************************************


Indices and tables
******************

* Index

* Module Index

* Search Page


PyCouchDB server
****************

class pycouchdb.server.Server(url='http://localhost', port=5984, user=None, password=None, ssl=None)

   Main class to connect to Database

   Parameters:
      * **url** (*str*) -- url to database server

      * **port** (*int*) -- port number for server connection defautl
        5984

      * **user** (*str*) -- user name

      * **password** (*str*) -- password

      * **ssl** (*bool*) -- use https

   Examples: >>> srv = Server() >>> srv.create('userdb') >>> users =
   srv.db('userdb') >>> usr = {'name': 'john', 'lastname':'doe'} >>>
   users.add(usr) >>> srv.delete('usersdb')

   all_dbs()

      Returns a list of all the databases in the CouchDB instance.

   create(name)

      Creates a new database. The database name {db} must be composed
      by following next rules: Name must begin with a lowercase letter
      (a-z) Lowercase characters (a-z) Digits (0-9) Any of the
      characters _, $, (, ), +, -, and /.

      Parameters:
         **name** (*str*) -- The name of new Db.

      Returns:
         status

      Return type:
         dict

      Raises:
         **ServerError** --

   db(name)

      Return interface to database

      Parameters:
         **name** (*str*) -- Database name

      Returns:
         instance of pychouch.db.Database:

      Return type:
         class

   dbs_info(*keys) -> list

      Returns information of a list of the specified databases in the
      CouchDB instance

      Parameters:
         **keys** (*list*) -- Array of database names to be requested

      Returns:
         list of datebase info

      Return type:
         list

      Raises:
         **ServerError** --

   delete(db_name)

      Deletes the specified database, and all the documents and
      attachments contained within it.

      Parameters:
         **db_name** (*str*) -- Database name

      Returns:
         status

      Return type:
         dict

      Raises:
         **ServerError** --

   membership()

      Displays the nodes that are part of the cluster as
      cluster_nodes. The field all_nodes displays all nodes this node
      knows about, including the ones that are part of the cluster.

      Returns:
      Return type:
         dict


PyCouchDB db
************

class pycouchdb.db.Database(name, server)

   add(doc, batch=False)

      Creates a new document in database

      Parameters:
         * **doc** (*dict*) -- Document ID.

         * **batch** (*bool*) -- Stores document in batch mode

      Returns:
         document id, revision

      Return type:
         tuple

      Raises:
         **DatabaseError** --

      You can write documents to the database at a higher rate by
      using the batch option. This collects document writes together
      in memory (on a per-user basis) before they are committed to
      disk. This increases the risk of the documents not being stored
      in the event of a failure, since the documents are not written
      to disk immediately.

   delete(docid)

      Marks the specified document as deleted

      Parameters:
         **docid** (*str*) -- Document ID

      Returns:
         document id rev

      Return type:
         tuple

      Raises:
         **DatabaseError** --

   doc_info(docid) -> dict

      Minimal amount of information about the specified document.

      Parameters:
         **docid** (*str*) -- Document ID.

      Returns:
         Dictionary with keys rev - revision, size - size of document
         , date

      Return type:
         dict

      Raises:
         **DatabaseError** --

   get(docid, attchments=False, att_encoding_info=False, atts_since=[], conflicts=False, deleted_conflicts=False, latest=False)

      Get docmument by id

      Parameters:
         * **docid** (*str*) -- Document ID

         * **attachments** (*bool*) -- Includes attachments bodies in
           response.Default is false

         * **att_encoding_info** (*bool*) -- Includes encoding

      Returns:
         Document

      Raises:
         **DatabaseError** --


PyCouchDB document
******************

class pycouchdb.doc.Document(dbobj, **kwargs)
