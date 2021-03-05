import urllib.error
from urllib.parse import urlparse
from urllib.parse import quote
from urllib.request import urlopen, Request
from threading import RLock
from base64 import b64encode
from http.client import HTTPResponse
from ..json import Json
from . import Connection , Response
from typing import Dict, Any

# TODO auth , connectionpool ?
class UrllibConn(Connection):
    def __init__(self, url:str = 'http://localhost:5984', timeout:int=5):
        self.lock = RLock()
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        url_data = urlparse(url)
        self.timeout = timeout
        self.user = url_data.username
        self.password = url_data.password
        self.url = f'{url_data.scheme}://{url_data.hostname}:{int(url_data.port or 5984)}'
       
        # self.errors_retryable = (errno.EPIPE, errno.ETIMEDOUT, errno.ECONNRESET, errno.ECONNREFUSED,
        #                          errno.ECONNABORTED, errno.EHOSTDOWN, errno.EHOSTUNREACH,
        #                          errno.ENETRESET, errno.ENETUNREACH, errno.ENETDOWN)
    
        if self.user and self.password:
            self.headers['Authorization'] = f"Basic {b64encode(f'{self.user}:{self.password}'.encode('utf-8')).decode('ascii')}"
    
    def get(self, path:str='', query:Dict[str,Any]={}):
        return self.request(method='GET', path=path, query=query)

    def post(self, path:str='', data:Any=None, headers:Dict[str, str]={}, query:Dict[str, Any]={}):
        return self.request(path, method='POST', data=data, headers=headers, query=query)

    def put(self, path:str='', data:Any=None, headers:Dict[str, str]={}, query:Dict[str, Any]={}):
        return self.request(path, method='PUT', data=data, headers=headers, query=query)

    def delete(self, path:str, query:Dict[str, Any]={}):
        return self.request(path, method='DELETE', query=query)

    def head(self, path:str, query:Dict[str, Any]={}):
        return self.request(path, method='HEAD', query=query)
    
    def request(self, path:str, method:str='GET', data:Any=None, headers:Dict[str, str]={}, query:Dict[str, Any]={}) -> Response:
        headers.update(self.headers)
        if type(data) is dict:
            data = Json.dumps(data)
            data = data.encode('utf8')
        _query:str = ""
        if query:
            _query = f"?{'&'.join([f'{k}={v}' for (k,v) in query.items()])}"
            
        req = Request(url=f'{self.url}/{quote(path)}{_query}', method=method, data=data, headers=headers)
        with self.lock:    
            # try:
            resp = urlopen(req)
            # data = resp.read()
            return UrllibResponse(resp)
            # except urllib.error.HTTPError as err:
            #     u = err
            #     print(u.status, u.getheaders(), u.msg, u.reason, dir(u))
            #     print(type(err), dir(err))
            #     return Response(err)

class UrllibResponse(Response):
    def __init__(self, resp: HTTPResponse):
        self.resp = resp
        self._headers = {}
        if resp.readable:
            self.body = resp.read()
            self._headers = resp.headers


    @property
    def status(self):
        return self.resp.status

    def get_data(self) -> Any:
        # try:
        return Json.loads(self.body.decode())
        # except json.JSONDecodeError:
        #     raise ServerError(self.body)

    def get_headers(self):
        return self.resp.headers