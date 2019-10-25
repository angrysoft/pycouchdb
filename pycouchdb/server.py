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
from urllib.request import urlopen, Request
import urllib.error
from base64 import b64encode
import json
from .db import Database
from threading import RLock


class Response:
    def __init__(self, resp):
        self.resp = resp
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


# TODO auth , connectionpool ?
class Session:
    def __init__(self, url, port, ssl=None, timeout=5, user=None, password=None):
        if user and password:
            pass
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        self.url = f'{url}:{port}'
        self.port = port
        self.timeout = timeout
        self.lock = RLock()
        self.ssl = ssl
        self.user = user
        self.password = password
        # self.errors_retryable = (errno.EPIPE, errno.ETIMEDOUT, errno.ECONNRESET, errno.ECONNREFUSED,
        #                          errno.ECONNABORTED, errno.EHOSTDOWN, errno.EHOSTUNREACH,
        #                          errno.ENETRESET, errno.ENETUNREACH, errno.ENETDOWN)
    
        if self.user and self.password:
            self.headers['Authorization'] = f"Basic {b64encode(f'{self.user}:{self.password}'.encode('utf-8')).decode('ascii')}"
        
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
            
        req = Request(url=f'{self.url}/{quote(path)}{_query}', method=method, data=data, headers=headers)
        with self.lock:    
            try:
                return Response(urlopen(req))
            except urllib.error.HTTPError as err:
                return Response(err)
       

class Server:
    """Main class to connect to Database"""
    
    def __init__(self, url='http://localhost', port=5984, user=None, password=None, ssl=None):
        """Class to create connection to db
        Kwargs:
            url (str): url to database server
            port (int): port number for server connection defautl 5984
        """
        self.session = Session(url=url, port=port, ssl=ssl, user=user, password=password)
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

    def dbs_info(self, *keys) -> list:
        """
        Returns information of a list of the specified databases in the CouchDB instance
        
        :param keys:
        :returns: list
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
        else:
            raise ServerError(resp.code)

    def create(self, name):
        """
        Creates a new database. 
        The database name {db} must be composed by following next rules:
        Name must begin with a lowercase letter (a-z)
        Lowercase characters (a-z)
        Digits (0-9)
        Any of the characters _, $, (, ), +, -, and /.
        
        Args:
            name (str):  The name of new Db.
        
        Returns:
            dict.  dict with {'ok': True}
        
        Raises:
            ServerError
            
        """
        # TODO : name check
        resp = self.session.put(path=name)
        if resp.code in (201, 202):
            return resp.json
        else:
            raise ServerError(resp.code)

    def delete(self, db_name):
        resp = self.session.delete(path=db_name)
        if resp.code in (200, 202):
            return resp.json
        else:
            raise ServerError(resp.code)
        
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
    _codes = {
        400: 'Invalid database name',
        401: 'CouchDB Server Administrator privileges required',
        404: 'Requested database not found',
        412: 'Database already exists'
        }
    
    def __init__(self, code=0, messeage=f'Unknow Error'):
        self.message = self._codes.get(code, messeage)    
        

