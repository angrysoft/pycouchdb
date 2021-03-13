import pytest
from pycouchdb.server import Server

srv = Server(url="http://admin:test@localhost")

def test_get_server_info():
    ret = srv.get_server_info()
    assert type(ret) == dict
    
def test_active_tasks():
    ret = srv.active_tasks()
    assert type(ret) == list

def test_list_database_names():
    ret = srv.list_database_names()
    assert type(ret) == list

def test_dbs_info():
    ret = srv.dbs_info()
    assert type(ret) == list
    