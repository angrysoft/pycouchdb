import json


class MetaDocument(type):

    def __new__(mcs, name, bases, attrs):
        result = type.__new__(mcs, name, bases, attrs)
        result.doc = dict()

        for obj_name in attrs:
            obj = getattr(result, obj_name)
            if not obj_name.startswith('_') and type(obj) is not 'function':
                result.doc[obj_name] = obj
        return result


class Document(metaclass=MetaDocument):
    _id = None
    _rev = None
    _doc = dict()

    def __init__(self, **kwargs):
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
