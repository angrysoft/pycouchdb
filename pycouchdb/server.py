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

from urllib.request import urlopen, Request
from urllib.parse import quote
import json
import urllib.error
from .db import Database


class Response:
    def __init__(self, resp):
        self.resp = resp
        self.body = None
        if resp.readable:
            self.body = resp.read()

    @property
    def code(self):
        return self.resp.code

    @property
    def status(self):
        return self.resp.status

    def json(self):
        try:
            return json.loads(self.body)
        except json.JSONDecodeError:
            raise ServerError(self.body)


class Session:
    def __init__(self, url, port):
        self.url = f'{url}:{port}'
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    def get(self, path=''):
        return self.request(method='GET', path=path)

    def post(self, path='', data=None, headers={}):
        return self.request(path, method='POST', data=data, headers=headers)

    def put(self, path='', data=None, headers={}):
        return self.request(path, method='PUT', data=data, headers=headers)

    def delete(self, path):
        return self.request(path, method='DELETE')

    def head(self, path):
        return self.request(path, method='HEAD')

    def request(self, path, method='GET', data=None, headers={}):
        headers.update(self.headers)
        if data is not None and type(data) is not str:
            try:
                data = json.dumps(data)
            except json.JSONDecodeError:
                raise ServerError(f'params parsing error {data}')
            data = data.encode('utf8')
            print('data', data)
        print(f'url : {self.url}/{quote(path)}')
        req = Request(url=f'{self.url}/{quote(path)}', method=method, data=data, headers=headers)
        try:
            return Response(urlopen(req))
        except urllib.error.HTTPError as err:
            print(err)
            return Response(err)

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
            print('debug:', err)
            return Response(err)


class Server:
    def __init__(self, url='http://localhost', port=5984, uesr=None, password=None):
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
        ret = resp.json()
        self._version = ret.get('version')
        self._uuid = ret.get('uuid')
        self._vendor = ret.get('vendor')

    def active_tasks(self):
        resp = self.session.get(path='_active_tasks')
        return resp.json()

    def all_dbs(self):
        resp = self.session.get(path='_all_dbs')
        return resp.json()

    def dbs_info(self, *keys):
        """
        Returns information of a list of the specified databases in the CouchDB instance
        :param keys
        :return list
        """
        _keys = list()
        _keys.extend(keys)
        try:
            resp = self.session.post(path='_dbs_info', data={'keys': _keys})
            return resp.json()
        except urllib.error.HTTPError:
            if self.version.startswith('1'):
                print('Error: minimum version server is 2.2')

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
        raise NotImplemented

    def membership(self):
        resp = self.session.get(path='_membership')
        return resp.json()

    def db(self, name):
        resp = self.session.head(path=name)
        if resp.code == 200:
            return Database(name, self)
        elif resp.code == 404:
            raise ServerError(f'Requested database not found:  {name}')

    def create(self, name):
        resp = self.session.put(path=name)
        if resp.code in (201, 202):
            return resp.json()
        elif resp.code == 400:
            raise ServerError('Bad Request – Invalid database name')
        elif resp.code == 401:
            raise ServerError('Unauthorized – CouchDB Server Administrator privileges required')
        elif resp.code == 412:
            raise ServerError('Precondition Failed – Database already exists')

    def delete(self, db_name):
        resp = self.session.delete(path=db_name)
        if resp.code in (200, 202):
            return resp.json()
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

