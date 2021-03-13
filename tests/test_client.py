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


@pytest.mark.order1
def test_create_db():
    _client.create('testdb')
    assert 'testdb' in _client


@pytest.mark.last
def test_delete_db():
    _client.delete('testdb')
    assert 'testdb' not in _client

    