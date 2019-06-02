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

    def __init__(self, **kwargs):
        self.update(kwargs)

    @classmethod
    def __str__(cls):
        return str(cls.doc)

    @classmethod
    def update(cls, _doc):
        if type(_doc) is not dict:
            raise ValueError('_doc should by a dict')
        for key in _doc:
            if key in cls.doc:
                cls.doc[key] = _doc[key]
            else:
                raise KeyError(f'{key} not in model')

    @property
    def json(self):
        return json.dumps(self.doc)

    @json.setter
    def json(self, value):
        self.update(json.loads(value))

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        if key in self.doc:
            self.doc[key] = value
        else:
            raise KeyError(f'{key} not in model')
