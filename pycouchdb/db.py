# Copyright 2019 AngrySoft Sebastian Zwierzchowski
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class Query:
    def __init__(self):
        pass


class Database:
    def __init__(self, name, server):
        self.server = server
        self.name = name

    def add(self, doc):
        resp = self.server.session.post(path=self.name, data=doc)
        if resp.code in (201, 202):
            ret = resp.json
            return ret.get('id'), ret.get('rev')
        elif resp.code == 400:
            raise DatabaseError('Bad Request – Invalid database name')
        elif resp.code == 401:
            raise DatabaseError('Unauthorized – Write privileges required')
        elif resp.code == 404:
            raise DatabaseError('Not Found – Database doesn’t exist')
        elif resp.code == 409:
            raise DatabaseError('Conflict – A Conflicting Document with same ID already exists')

    def doc(self, _id, attchment=False):
        if attchment:
            headers = {'Accept': 'multipart/related'}

        resp = self.server.session.get(f'{self.name}/{_id}')
        if resp.code in (200, 304):
            return resp.json()
        elif resp.code == 400:
            raise DatabaseError('The format of the request or revision was invalid')
        elif resp.code == 401:
            raise DatabaseError('Read privilege required')
        elif resp.code == 404:
            return {}

    def all_doc(self, *keys):
        path = f'{self.name}/_all_docs'
        _keys = list()
        _keys.extend(keys)
        if keys:
            resp = self.server.session.post(path, data={"keys": _keys})
        else:
            resp = self.server.session.get(path)
        return resp.json()

    def find(self, selector=None, fields=[], sort=[], limit=25, skip=0, execution_status='true'):
        raise NotImplementedError
        test = {
            "selector": {
                "model": {"$eq": "plug"}
            },
            "fields": ["_id", "_rev", "model", "name"],
            "sort": [{"name": "asc"}],
            "limit": 2,
            "skip": 0,
            "execution_stats": True
        }
        path = f'{self.name}/_find'
        resp = self.server.session.post(path=path, data=test)
        if resp.code == 200:
            return resp.json()
        elif resp.code == 401:
            raise DatabaseError('Read permission required')
        elif resp.code == 500:
            raise DatabaseError('Query execution error')

    def bulk_get(self):
        path = f'{self.name}/_bulk_get'
        resp = self.server.session.post(path=path, data={"docs": []}, headers={'Content-Type': 'application/json'})
        if resp.code == 200:
            print('bulk')
            return resp.json()

    def __contains__(self, item):
        resp = self.server.session.head(path=f'{self.name}/{item}')
        if resp.code == 200:
            return True
        else:
            return False

    def __iter__(self):
        doc = self.all_doc()
        self.rows = doc.get('rows')
        self.i = 0
        return self

    def __next__(self):
        if self.i <= (len(self.rows)-1):
            doc = self.rows[self.i]
            print(f'aaa {doc}')
            self.i += 1
            return self[doc['id']]
        else:
            raise StopIteration

    def __getitem__(self, item):
        return self.doc(item)

    def __setitem__(self, key, value):
        value['_id'] = key
        self.add(value)


class DatabaseError(Exception):
    def __init__(self, status, code=0):
        msg = {
            400: 'Invalid database name',
            401: 'CouchDB Server Administrator privileges required',
            412: 'Database already exists'
               }
        self.message = msg.get(status, f'Unknow Error: {status}')


class DocumentError(Exception):
    pass