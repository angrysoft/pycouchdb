from pycouchdb.db import FindQuery
import pytest
from pycouchdb.client import Client

_client = Client('http://admin:test@localhost')

docs_list = [{'number': 1, 'name': 'one', 'type': 'number'},
             {'number': 2, 'name': 'two', 'type': 'number'},
             {'number': 3, 'name': 'three', 'type': 'number'},
             {'number': 4, 'name': 'four', 'type': 'number'},
             {'number': 5, 'name': 'five', 'type': 'number'},
             {'letter': 'a', 'name': 'a', 'type': 'letter'},
             {'letter': 'b', 'name': 'b', 'type': 'letter'},
             {'letter': 'c', 'name': 'c', 'type': 'letter'},
             {'letter': 'd', 'name': 'd', 'type': 'letter'},
             {'letter': 'e', 'name': 'e', 'type': 'letter'}]



def test_create_db():
    _client.create('testdb')
    assert 'testdb' in _client


def test_add_document():
        for i, d in enumerate(docs_list):
            d['_id'] = str(i)
            db = _client.get_db('testdb')
            assert type(db.add(d)) is tuple


def test_update_document():
        db = _client.get_db('testdb')
        db.update('0', {'name': 'oneone'})
        db['1'] = {'name': 'twotwo'}
        db['123'] = {'name': 'notexists'}


def test_get_document():
    db = _client.get_db('testdb')
    assert db['0']['name'] is str


def test_find_documents():
    db = _client.get_db('testdb')
    query = FindQuery()
    query.selector['type'] = 'number'
    ret = db.find(query)
    assert len(ret) == 5


def test_delete_db():
    _client.delete('testdb')
    assert 'testdb' not in _client