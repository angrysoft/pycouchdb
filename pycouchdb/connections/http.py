from urllib.parse import urlparse
from base64 import b64encode
from threading import RLock
from . import Connection, Response
from ..json import Json
from urllib.parse import quote
from typing import Dict, Any
import http.client


class HttpClientConn(Connection):
    def __init__(self, url: str, timeout:int = 5) -> None:
        self.lock = RLock()
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        self.url_data = urlparse(url)
        self.timeout = timeout
        self.user = self.url_data.username
        self.password = self.url_data.password
        
        # self.errors_retryable = (errno.EPIPE, errno.ETIMEDOUT, errno.ECONNRESET, errno.ECONNREFUSED,
        #                          errno.ECONNABORTED, errno.EHOSTDOWN, errno.EHOSTUNREACH,
        #                          errno.ENETRESET, errno.ENETUNREACH, errno.ENETDOWN)
        
        if self.user and self.password:
            self.headers['Authorization'] = f"Basic {b64encode(f'{self.user}:{self.password}'.encode('utf-8')).decode('ascii')}"
        
        self.conn = self._make_conn()
    
    def _make_conn(self):
        if self.url_data.scheme == 'https':
            return http.client.HTTPSConnection(self.url_data.hostname or "localhost",
                                               port=self.url_data.port or 5984,
                                               timeout=self.timeout)
        else:
            return http.client.HTTPConnection(self.url_data.hostname or "localhost",
                                              port=self.url_data.port or 5984,
                                              timeout=self.timeout)
    
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
    
    def request(self, path:str, method:str='GET', data:Any=None, headers:Dict[str, str]={}, query:Dict[str, Any]={}, retry:int=3) -> Response:
        headers.update(self.headers)
        if type(data) is dict:
            data = Json.dumps(data)
            data = data.encode('utf8')
        _query:str = ""
        if query:
            _query = f"?{'&'.join([f'{k}={v}' for (k,v) in query.items()])}"
        
        with self.lock:
            try:
                self.conn.request(method=method, url=f'/{quote(path)}{_query}', body=data, headers=headers)
                resp = self.conn.getresponse()
                # self.conn.close()
                return HTTPClientResponse(resp.status, resp.getheaders(), data=resp.read())
            except BrokenPipeError:
                self.conn = self._make_conn()
                if retry > 0:
                    return self.request(path=path, method=method, data=data, headers=headers, query=query, retry=retry-1)
                
    def __del__(self):
        self.conn.close()
        

class HTTPClientResponse(Response):
    def __init__(self, status:int, headers:Any = {},  data: Any = ''):
        self._status = status
        self._headers = headers
        self._data = data


    @property
    def status(self):
        return self._status

    def get_data(self) -> Any:
        # try:
        ret = {}
        if self._data:
            ret = Json.loads(self._data)
        return ret
        # except json.JSONDecodeError:
        #     raise ServerError(self.body)

    def get_headers(self):
        return dict(self._headers)