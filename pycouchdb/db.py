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


class Databese:
    def __init__(self,name, server):
        self.server = server
        self.name = name

    def insert(self, doc):
        status, ret = self.server._post(path=self.name, data=doc)
        if status in (201, 202):
            ret = self.server._jload(ret)
            return ret.get('id'), ret.get('rev')
        elif status == 400:
            raise DatabaseError('Bad Request – Invalid database name')
        elif status == 401:
            raise DatabaseError('Unauthorized – Write privileges required')
        elif status == 404:
            raise DatabaseError('Not Found – Database doesn’t exist')
        elif status == 409:
            raise DatabaseError('Conflict – A Conflicting Document with same ID already exists')

    def all_doc(self):
        status, ret = self.server._get(path=f'{self.name}/_all_doc')
        return self.server._jload(ret)


class DatabaseError(Exception):
    def __init__(self, status):
        msg = {
            400: 'Invalid database name',
            401: 'CouchDB Server Administrator privileges required',
            412: 'Database already exists'
               }
        self.message = msg.get(status, f'Unknow Error: {status}')