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
from urllib.parse import urlencode
import json
import urllib.error
from .db import Database


class Server:
    def __init__(self, url='http://localhost', port=5984):
        self.url = f'{url}:{port}'
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

    @staticmethod
    def _jload(data):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise ServerError('data')

    @staticmethod
    def _jdump(data):
        try:
            return json.dumps(data)
        except json.JSONDecodeError:
            raise ServerError('data')

    def _get_server_info(self):
        status, ret = self._get()
        ret = self._jload(ret)
        self._version = ret.get('version')
        self._uuid = ret.get('uuid')
        self._vendor = ret.get('vendor')

    def active_tasks(self):
        status, ret = self._get(path='_active_tasks')
        return self._jload(ret)

    def all_dbs(self):
        status, ret = self._get(path='_all_dbs')
        return self._jload(ret)

    def dbs_info(self, *keys):
        """
        Returns information of a list of the specified databases in the CouchDB instance
        :param keys
        :return list
        """
        _keys = list()
        _keys.extend(keys)
        try:
            status, ret = self._post(path='', data=json.dumps(_keys))
            return self._jload(ret)
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
        status, ret = self._get(path='_membership')
        return self._jload(ret)

    def _get(self, path=''):
        return self._request(method='GET', path=path)

    def _post(self, path='', data=None, headers={}):
        if data:
            data = data.encode()
        return self._request(path, method='POST', data=data, headers=headers)

    def _put(self, path='', data=None, headers={}):
        if data:
            data = data.encode()
        return self._request(path, method='PUT', data=data, headers=headers)

    def _delete(self, path):
        return self._request(path, method='DELETE')

    def _head(self, path):
        return self._request(path, method='HEAD')

    def _request(self, path, method='GET', data=None, headers={}):
        req = Request(url=f'{self.url}/{path}', method=method, data=data, headers=headers)
        try:
            r = urlopen(req)
            if r.readable:
                return r.code, r.read()
        except urllib.error.HTTPError as err:
            print(err)
            return err.code, None

    def db(self, name):
        status, ret = self._head(path=name)
        if status == 200:
            return Database(name, self)
        elif status == 404:
            raise ServerError(f'Requested database not found:  {name}')

    def create(self, name):
        status, ret = self._put(path=name)
        if status in (201, 202):
            return self._jload(ret)
        elif status == 400:
            raise ServerError('Bad Request – Invalid database name')
        elif status == 401:
            raise ServerError('Unauthorized – CouchDB Server Administrator privileges required')
        elif status == 412:
            raise ServerError('Precondition Failed – Database already exists')

    def delete(self, db_name):
        status ,ret = self._delete(path=db_name)
        if status in (200, 202):
            return self._jload(ret)
        elif status == 400:
            raise ServerError('Bad Request – Invalid database name or forgotten document id by accident')
        elif status == 401:
            raise ServerError('Unauthorized – CouchDB Server Administrator privileges required')
        elif status == 404:
            raise ServerError('Not Found – Database doesn’t exist or invalid database name')


class ServerError(Exception):
    pass

