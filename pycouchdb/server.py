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

from urllib.parse import quote
import json
from .db import Database
import http.client


class Response:
    def __init__(self, resp):
        self.resp = resp
        self.body = None
        self._headers = {}
        if resp.readable:
            self.body = resp.read()
            self._headers = resp.headers

    @property
    def code(self):
        return self.resp.code

    @property
    def status(self):
        return self.resp.status

    @property
    def json(self):
        try:
            return json.loads(self.body)
        except json.JSONDecodeError:
            raise ServerError(self.body)

    @property
    def headers(self):
        return self.resp.headers


class Session:
    def __init__(self, url, port, ssl=None):
        self.url = f'{url}:{port}'
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        if ssl:
            self.conn = http.client.HTTPSConnection(url, port, timeout=2)
        else:
            self.conn = http.client.HTTPConnection(url, port, timeout=2)

    def get(self, path='', query={}):
        return self.request(method='GET', path=path, query=query)

    def post(self, path='', data=None, headers={}, query={}):
        return self.request(path, method='POST', data=data, headers=headers, query=query)

    def put(self, path='', data=None, headers={}, query={}):
        return self.request(path, method='PUT', data=data, headers=headers, query=query)

    def delete(self, path, query={}):
        return self.request(path, method='DELETE', query=query)

    def head(self, path, query={}):
        return self.request(path, method='HEAD', query=query)

    def request(self, path, method='GET', data=None, headers={}, query={}):
        headers.update(self.headers)
        _query = '&'.join([f'{q}={query[q]}' for q in query])
        if data is not None and type(data) is not str:
            try:
                data = json.dumps(data)
            except json.JSONDecodeError:
                raise ServerError(f'params parsing error {data}')
            data = data.encode('utf8')
        if query:
            _query = f'?{_query}'
        
        self.conn.request(method, f'/{quote(path)}{_query}',  body=data, headers=headers)
        return Response(self.conn.getresponse())

    def __del__(self):
        self.conn.close()


    @staticmethod
    def jload(data):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise ServerError('data')

    @staticmethod
    def jdump(data):
        try:
            return json.dumps(data)
        except json.JSONDecodeError:
            raise ServerError('data')


class Server:
    def __init__(self, url='localhost', port=5984, uesr=None, password=None):
        self.session = Session(url=url, port=port)
        self._version = None
        self._uuid = None
        self._vendor = None
        self._get_server_info()

    @property
    def version(self):
        return self._version

    @property
    def uuid(self):
        return self._uuid

    @property
    def vendor(self):
        return self._vendor

    def _get_server_info(self):
        resp = self.session.get()
        ret = resp.json
        self._version = ret.get('version')
        self._uuid = ret.get('uuid')
        self._vendor = ret.get('vendor')

    def active_tasks(self):
        resp = self.session.get(path='_active_tasks')
        return resp.json

    def all_dbs(self):
        resp = self.session.get(path='_all_dbs')
        return resp.json

    def dbs_info(self, *keys):
        """
        Returns information of a list of the specified databases in the CouchDB instance
        :param keys
        :return list
        """
        _keys = list()
        _keys.extend(keys)
        resp = self.session.post(path='_dbs_info', data={'keys': _keys})
        return resp.json

    def cluster_setup(self):
        pass

    def db_updates(self, feed=None, timeout=None, heartbeat=None, since=None):
        args = dict()
        if feed:
            args['feed'] = feed
        if timeout:
            args['timeout'] = timeout
        if heartbeat:
            args['heartbeat'] = heartbeat
        if since:
            args['since'] = since
        raise NotImplementedError

    def membership(self):
        resp = self.session.get(path='_membership')
        return resp.json

    def db(self, name):
        resp = self.session.head(path=name)
        if resp.code == 200:
            return Database(name, self)
        elif resp.code == 404:
            raise ServerError(f'Requested database not found:  {name}')

    def create(self, name):
        # TODO : name check
        resp = self.session.put(path=name)
        if resp.code in (201, 202):
            return resp.json
        elif resp.code == 400:
            raise ServerError('Bad Request – Invalid database name')
        elif resp.code == 401:
            raise ServerError('Unauthorized – CouchDB Server Administrator privileges required')
        elif resp.code == 412:
            raise ServerError('Precondition Failed – Database already exists')

    def delete(self, db_name):
        resp = self.session.delete(path=db_name)
        if resp.code in (200, 202):
            return resp.json
        elif resp.code == 400:
            raise ServerError('Bad Request – Invalid database name or forgotten document id by accident')
        elif resp.code == 401:
            raise ServerError('Unauthorized – CouchDB Server Administrator privileges required')
        elif resp.code == 404:
            raise ServerError('Not Found – Database doesn’t exist or invalid database name')

    def __iter__(self):
        return iter(self.all_dbs())

    def __getitem__(self, item):
        return self.db(item)

    def __contains__(self, item):
        resp = self.session.head(path=item)
        if resp.code == 200:
            return True
        else:
            return False


class ServerError(Exception):
    pass

