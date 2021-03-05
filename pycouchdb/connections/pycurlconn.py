from urllib.parse import urlparse
import pycurl
from io import BytesIO
from base64 import b64encode
from threading import RLock
from . import Connection, Response
from ..json import Json
from urllib.parse import quote
from typing import Dict, Any


class PyCurlConn(Connection):
    def __init__(self, url: str, timeout:int = 5) -> None:
        self.lock = RLock()
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        url_data = urlparse(url)
        self.timeout = timeout
        self.user = url_data.username
        self.password = url_data.password
        self.url = f'{url_data.scheme}://{url_data.hostname}:{int(url_data.port or 5984)}'
        self.curl = pycurl.Curl()
       
        # self.errors_retryable = (errno.EPIPE, errno.ETIMEDOUT, errno.ECONNRESET, errno.ECONNREFUSED,
        #                          errno.ECONNABORTED, errno.EHOSTDOWN, errno.EHOSTUNREACH,
        #                          errno.ENETRESET, errno.ENETUNREACH, errno.ENETDOWN)
    
        if self.user and self.password:
            self.headers['Authorization'] = f"Basic {b64encode(f'{self.user}:{self.password}'.encode('utf-8')).decode('ascii')}"
    
    def get(self, path: str, query: Dict[str, Any]) -> Response:
        buffer = BytesIO()
        self.set_url(path=path, query=query)
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        self.curl.perform()
        self.curl.close()
        return PyCurlResponse(self.curl.getinfo(pycurl.HTTP_CODE), buffer.getvalue())
    
    def post(self, path: str, data: Any, headers: Dict[str, str], query: Dict[str, Any]) -> Response:
        buffer = BytesIO()
        self.set_url(path=path, query=query)
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        self.curl.setopt(pycurl.POSTFIELDS, self.set_data(data))
        self.curl.perform()
        self.curl.close()
        return PyCurlResponse(self.curl.getinfo(pycurl.HTTP_CODE), buffer.getvalue())
    
    def put(self, path: str, data: Any, headers: Dict[str, str], query: Dict[str, Any]) -> Response:
        buffer = BytesIO()
        self.set_url(path=path, query=query)
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        self.curl.setopt(pycurl.POSTFIELDS, self.set_data(data))
        self.curl.perform()
        self.curl.close()
        return PyCurlResponse(self.curl.getinfo(pycurl.HTTP_CODE), buffer.getvalue())
    
    def delete(self, path: str, query: Dict[str, Any]) -> Response:
        return super().delete(path, query=query)
    
    def head(self, path: str, query: Dict[str, Any]) -> Response:
        return super().head(path, query=query)
    
    def set_data(self, data:Any):
        if type(data) is dict:
            data = Json.dumps(data)
            data = data.encode('utf8')
        return data
    
    def set_url(self, path:str, headers:Dict[str, str]={}, query:Dict[str, Any]={}) -> None:
        headers.update(self.headers)
        
        _query:str = ""
        if query:
            _query = f"?{'&'.join([f'{k}={v}' for (k,v) in query.items()])}"
            
        # req = Request(url=f'{self.url}/{quote(path)}{_query}', method=method, data=data, headers=headers)
        self.curl.setopt(pycurl.URL, f'{self.url}/{quote(path)}{_query}')
        if headers:
            self.curl.setopt(pycurl.HTTPHEADER, [f'{k}={v}' for (k,v) in headers.items()])


class PyCurlResponse(Response):
    def __init__(self, status:int, data:Any) -> None:
        self._status = status
        self._data = data
        
    @property
    def status(self) -> int:
        return self._status
    
    def get_data(self) -> Any:
         return Json.loads(self._data) 
    
    def get_headers(self) -> Any:
        return super().get_headers()
        
    