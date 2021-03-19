import pytest
from pycouchdb.doc import Document

@pytest.fixture
def doc() -> Document:
    return Document({"a": 1, "b": 2, "c": 3})

def test_create_doc_from_dict(doc: Document):
    assert doc["a"] == 1

def test_update_dict(doc: Document):
    doc.update({"a": 5})
    doc.update(b=4)
    assert doc["a"] == 5
    assert doc["b"] == 4

def test_len(doc: Document):
    assert len(doc) == 3

def test_delete(doc: Document):
    del doc["a"]
    assert len(doc) == 2

def test_popitem(doc: Document):
    k, v = doc.popitem()
    assert k == 'c'
    assert v == 3
    assert len(doc) == 2

def test_pop(doc: Document):
    v = doc.pop("b")
    nonexist = doc.pop('nonexist', 'nonexist')
    assert v == 2
    assert nonexist == 'nonexist'
    assert len(doc) == 2

def test_json(doc: Document):
    assert doc.json == '{"a": 1, "b": 2, "c": 3}'

def test_iter(doc: Document):
    result = 0
    for k in doc:
        result += doc[k]
    assert result == 6

def test_items(doc: Document):
    result = 0
    for _,v in doc.items():
        result += v
    assert result == 6