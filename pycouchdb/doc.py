from collections.abc import MutableMapping
from pycouchdb.db import Database
from .json import Json
from typing import Any, Optional, Dict

class DocumentList:
    pass

class Document(MutableMapping):
    def __init__(self, db: Optional[Database] = None, **kwargs:str) -> None:
        self._doc:Dict[str, Any] = {}
        if kwargs:
            self.update(kwargs)
        self._db = db
    
    @property
    def id(self) -> str:
        return self._doc.get('_id', '')
    
    @id.setter
    def id(self, value:str):
        self._doc['_id'] = value
        
    @property
    def rev(self) -> str:
        return self._doc.get('_rev', '')
    
    @rev.setter
    def rev(self, value:str):
        self._doc['_rev'] = value
    
    def __str__(self) -> str:
        return str(self._doc)
    
    def update(self, **kwargs:str) -> None:
        self._doc.update(kwargs)
        
    

class _Document:
    
    @classmethod
    def from_dict(cls, data, db=None):
        obj = cls.__new__(cls)
        instance = cls(db)
        instance.update(data)
        return instance

    def __init__(self, db=None, **kwargs):
        self._doc = dict()
        if kwargs:
            self.update(kwargs)
        self._db = db
        # if isinstance(db, Database):
        #     self._db = db
    
    @property
    def id(self):
        return self._doc.get('_id')
    
    @id.setter
    def id(self, value):
        self._doc['_id'] = value
        
    @property
    def rev(self):
        return self._doc('_rev')
    
    @rev.setter
    def rev(self, value):
        self._doc['_rev'] = value
    
    def __str__(self):
        return str(self._doc)

    def update(self, _doc):
        if type(_doc) is not dict:
            raise ValueError('_doc should by a dict')
        self._doc.update(_doc)
    
    def pop(self, key, default=None):
        return self._doc.pop(key, default)
    
    def popitem(self):
        return self._doc.popitem()

    @property
    def json(self):
        return json.dumps(self._doc)

    @json.setter
    def json(self, value):
        self.update(json.loads(value))
        
    def get_dict(self):
        return self._doc.copy()
    
    def get(self, key, default=None):
        return self._doc.get(key, default)

    def __getitem__(self, key):
        return self._doc[key]

    def __setitem__(self, key, value):
        self._doc[key] = value

  
