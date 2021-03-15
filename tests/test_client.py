from typing import Dict, List, Any
import pytest
from pycouchdb.db import Database
from pycouchdb.query import FindQuery, IndexQuery
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


@pytest.fixture
def db() -> Database:
    return _client.get_db('testdb')


def test_create_db():
    _client.create('testdb')
    assert 'testdb' in _client


def test_add_document(db: Database):
        for i, d in enumerate(docs_list):
            d['_id'] = str(i)
            assert type(db.add(d)) is tuple


def test_update_document(db: Database):
        db.update('0', {'name': 'oneone'})
        db['1'] = {'name': 'twotwo'}
        db['123'] = {'name': 'notexists'}


def test_get_document(db: Database):
    assert db['0']['name'] == 'oneone'

def test_set_index(db: Database):
    index = IndexQuery()
    index.fields.append('type')
    index.name = "test_type_index"
    ret = db.set_index(index)
    assert ret.get('result') == 'created'

def test_get_index(db: Database):
    ret: Dict[str, Any] = db.get_indexes()
    assert "indexes" in ret

def test_delete_index(db: Database):
    indexes = db.get_indexes()
    _design = ''
    for ddoc in indexes['indexes']:
        if ddoc['name'] == "test_type_index":
            _design = ddoc['ddoc']
            break
    ret = db.delete_index(design=_design, name="test_type_index")
    assert ret.get('ok')

def test_find_documents(db: Database):
    query = FindQuery()
    query.selector['type'] = 'number'
    ret = db.find(query)
    assert len(ret.get('docs')) == 5
    

def test_delete_document(db: Database):
    for i, d in enumerate(docs_list):
        d['_id'] = str(i)
        assert type(db.delete(str(i))) is tuple
        
def test_add_many_documents(db: Database):
    ret = db.add_many(docs_list)
    assert len(ret) == 10
    
def test_get_many_documents(db: Database):
    ret = db.get_many([{"id": str(x)} for x in range(0,10)])
    assert len(ret) == 10
    
def test_update_many_documents(db: Database):
    docs = db.get_many([{"id": str(x)} for x in range(0,10)])
    docs_to_update: List[Dict[str, Any]] = []
    
    for i, x in enumerate(docs):
        doc = x['docs'][0].get('ok', {})
        doc['n'] = i
        docs_to_update.append(doc)
        
    ret = db.update_many(docs_to_update)
    assert len(ret) == 10

def test_delete_db():
    _client.delete('testdb')
    assert 'testdb' not in _client