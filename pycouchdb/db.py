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
import json

class Query:
    def __init__(self):
        pass


class Database:
    def __init__(self, name, server):
        self.server = server
        self.name = name

    def insert(self, doc):
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

    def all_doc(self, *keys):
        path = f'{self.name}/_all_docs'
        if keys:
            resp = self.server.session.post(path, data=json.dumps({"keys": keys}))
        else:
            resp = self.server.session.get(path)
        return resp.json()

    def find(self, selector=None, fields=[], sort=[], limit=25, skip=0, execution_status='true'):
        # {
        #     "selector": {
        #         "year": {"$gt": 2010}
        #     },
        #     "fields": ["_id", "_rev", "year", "title"],
        #     "sort": [{"year": "asc"}],
        #     "limit": 2,
        #     "skip": 0,
        #     "execution_stats": true
        # }
        path = f'{self.name}/_find'
        if selector is None:
            status, ret = self.server.session.post(path=path)
        else:
            pass

    def __contains__(self, item):
        resp = self.server.session.head(path=f'{self.name}/{item}')
        if resp.code == 200:
            return True
        else:
            return False


class DatabaseError(Exception):
    def __init__(self, status):
        msg = {
            400: 'Invalid database name',
            401: 'CouchDB Server Administrator privileges required',
            412: 'Database already exists'
               }
        self.message = msg.get(status, f'Unknow Error: {status}')