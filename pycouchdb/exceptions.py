class ServerError(Exception):
    _codes = {
        400: 'Invalid database name',
        401: 'CouchDB Server Administrator privileges required',
        404: 'Requested database not found',
        412: 'Database already exists'
        }
    
    def __init__(self, code=0, messeage=f'Unknow Error'):
        self.message = self._codes.get(code, messeage)
        

class DatabaseError(Exception):
    _codes = {
            400: 'Invalid database name',
            401: 'Read/Write privileges required',
            404: 'Requested database not found',
            409: 'A Conflicting Document with same ID already exists',
            412: 'Database already exists',
            415: 'Bad Content-Type value',
            417: 'Expectation Failed – Occurs when at least one document was rejected by a validation function',
            500: 'Query execution error'
               }
    
    def __init__(self, code=0, messeage=f'Unknow Error'):
        self.message = self._codes.get(code, messeage)   


class DocumentError(Exception):
    _codes = {}
    
    def __init__(self, code=0, messeage=f'Unknow Error'):
        self.message = self._codes.get(code, messeage)


