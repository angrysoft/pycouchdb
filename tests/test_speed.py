#!/usr/bin/python3
from typing import Any, Dict, List
import pytest
from pycouchdb.client import Client
from pycouchdb.connections.http import HttpClientConn
from pycouchdb.connections.urllibcon import UrllibConn


_client = Client('http://admin:test@localhost', connection_engine=UrllibConn)
db_name = "speedtestdb"
if db_name in _client:
    _client.delete(db_name)
_client.create(db_name)
db = _client.get_db(db_name)
doc = {'number': 1, 'name': 'one', 'type': 'number'}
_to = 500

def db_add():
    for i in range(0, _to):
        doc['_id'] = f'{i:03d}'
        db.add(doc)
        
            
def db_get():
    ret: List[Dict[str, Any]] = []
    for i in range(0, _to):
        ret.append(db[f'{i:03d}'])
    return ret

def db_del():
    for i in range(0, _to):
        db.delete(f'{i:03d}')
    _client.delete(db_name)

def test_add(benchmark):
    benchmark.pedantic(db_add, iterations=1)

def test_get(benchmark):
    result = benchmark.pedantic(db_get, iterations=1)
    assert len(result) == _to

def test_del(benchmark):
    benchmark.pedantic(db_del, iterations=1)
