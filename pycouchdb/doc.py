import json

class DocumentList:
    pass

class Document: #(metaclass=MetaDocument):
    
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

    @property
    def json(self):
        return json.dumps(self._doc)

    @json.setter
    def json(self, value):
        self.update(json.loads(value))
        
    def get_dict(self):
        return self._doc.copy()

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        self._doc[key] = value

class DocumentError(Exception):
    _codes = {}
    
    def __init__(self, code=0, messeage=f'Unknow Error'):
        self.message = self._codes.get(code, messeage)   
