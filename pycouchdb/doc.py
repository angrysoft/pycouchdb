from collections.abc import MutableMapping
from .exceptions import DocumentError
from .db import Database
from .json import Json
from typing import Any, Iterator, Optional, Dict

class DocumentList:
    pass

class Document(MutableMapping):
    """ Document class"""
    def __init__(self, _dict:Optional[Dict[Any,Any]] = None, **kwargs:str) -> None:
        self._doc:Dict[str, Any] = {}
        
        if _dict is not None:
           self.update(_dict) 
        
        if kwargs:
            self.update(kwargs)
            
        self._db: Optional[Database] = None
    
    @property
    def db(self) -> Database:
        """Database instance"""
        if self._db is None:
            raise DocumentError('Database is not set')
        return self._db
    
    @db.setter
    def db(self, db_instace: Database):
        self._db = db_instace
    
    @property
    def id(self) -> str:
        """Document id"""
        return self._doc.get('_id', '')
    
    @id.setter
    def id(self, value:str):
        self._doc['_id'] = value
        
    @property
    def rev(self) -> str:
        """Document revision"""
        return self._doc.get('_rev', '')
    
    @rev.setter
    def rev(self, value:str):
        self._doc['_rev'] = value
    
    @property
    def json(self) -> str:
        """serialized to json string"""
        return Json.dumps(self._doc)
    
    def pop(self, key:str, default: Any=None) -> Any:
        return self._doc.pop(key, default)
    
    def popitem(self) -> Any:
        return self._doc.popitem()
    
    def store(self):
        """Store document to databse if databse instance is set else raise DocumentError"""
        self._db.update(self.id, self._doc, rev=self.rev)
        
    def store_to_databse(self, db:Database):
        """Store document to given database instace"""
        db.update(self.id, self._doc, rev=self.rev)
    
    def load_from_database(self, db: Database, doc_id:str, doc_rev:str = ''):
        """Load document from given database instance and set db as current"""
        doc = db.get(doc_id, rev=doc_rev)
        self.id = doc.pop("_id", "")
        self.rev = doc.pop("_rev", "")
        self.db = db
        self._doc.update(doc)
                            
    def __str__(self) -> str:
        return f"<Document {self._doc}>"
        
    def __getitem__(self, key: str) -> Any:
        return self._doc[key]

    def __setitem__(self, key: str, value: Any):
        self._doc[key] = value
    
    def __delitem__(self, v: str) -> None:
        del self._doc[v]
        
    def __len__(self) -> int:
        return len(self._doc)
    
    def __iter__(self) -> Iterator[Any]:
        return self._doc.__iter__()
