import json

class DocumentList:
    pass

class Document: #(metaclass=MetaDocument):

    def __init__(self, dbobj=None, **kwargs):
        self._id = None
        self._rev = None
        self._doc = dict()
        self.update(kwargs)

    @classmethod
    def __str__(cls):
        return str(cls._doc)

    @classmethod
    def update(cls, _doc):
        if type(_doc) is not dict:
            raise ValueError('_doc should by a dict')
        for key in _doc:
            cls._doc[key] = _doc[key]

    @property
    def json(self):
        return json.dumps(self._doc)

    @json.setter
    def json(self, value):
        self.update(json.loads(value))

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
            self._doc[key] = value

class DocumentError(Exception):
    _codes = {}
    
    def __init__(self, code=0, messeage=f'Unknow Error'):
        self.message = self._codes.get(code, messeage)   
