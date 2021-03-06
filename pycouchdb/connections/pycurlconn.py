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
        self.curl = None
        if self.user and self.password:
            self.headers['Authorization'] = f"Basic {b64encode(f'{self.user}:{self.password}'.encode('utf-8')).decode('ascii')}"
    
    def get(self, path: str, query: Dict[str, Any]) -> Response:
        buffer = BytesIO()
        ret = PyCurlResponse()
        self.curl = pycurl.Curl()
        self.set_url(path=path, query=query)
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        self.curl.perform()
        ret.set_status(self.curl.getinfo(pycurl.HTTP_CODE))
        ret.set_data(buffer.getvalue())
        self.curl.close()
        return ret
    
    def post(self, path: str, data: Any, headers: Dict[str, str] = {}, query: Dict[str, Any] = {}) -> Response:
        buffer = BytesIO()
        self.curl = pycurl.Curl()
        self.set_url(path=path, query=query)
        ret = PyCurlResponse()
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        if data:
            self.curl.setopt(pycurl.POSTFIELDS, self.set_data(data))
        self.curl.perform()
        ret.set_status(self.curl.getinfo(pycurl.HTTP_CODE))
        ret.set_data(buffer.getvalue())
        self.curl.close()
        return ret
    
    def put(self, path: str, data: Any = {}, headers: Dict[str, str] = {}, query: Dict[str, Any] = {}) -> Response:
        buffer = BytesIO()
        ret = PyCurlResponse()
        self.curl = pycurl.Curl()
        self.set_url(path=path, query=query)
        self.curl.setopt(pycurl.HEADERFUNCTION, ret.put_header)
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        self.curl.setopt(pycurl.CUSTOMREQUEST, 'PUT')
        if data:
            self.curl.setopt(pycurl.POSTFIELDS, self.set_data(data))
        self.curl.perform()
        ret.set_status(self.curl.getinfo(pycurl.HTTP_CODE))
        ret.set_data(buffer.getvalue())
        self.curl.close()
        return ret
    
    def delete(self, path: str, query: Dict[str, Any] = {}) -> Response:
        buffer = BytesIO()
        self.curl = pycurl.Curl()
        ret = PyCurlResponse()
        self.set_url(path=path, query=query)
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        self.curl.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
        self.curl.perform()
        ret.set_status(self.curl.getinfo(pycurl.HTTP_CODE))
        ret.set_data(buffer.getvalue())
        self.curl.close()
        return ret
    
    def head(self, path: str, query: Dict[str, Any] = {}) -> Response:
        buffer = BytesIO()
        ret = PyCurlResponse()
        self.curl = pycurl.Curl()
        self.set_url(path=path, query=query)
        self.curl.setopt(pycurl.HEADERFUNCTION, ret.put_header)
        self.curl.setopt(pycurl.NOBODY, True)
        self.curl.perform()
        ret.set_status(self.curl.getinfo(pycurl.HTTP_CODE))
        ret.set_data(buffer.getvalue())
        self.curl.close()
        return ret
        
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
            
        self.curl.setopt(pycurl.URL, f'{self.url}/{quote(path)}{_query}')
        if headers:
            self.curl.setopt(pycurl.HTTPHEADER, [f'{k}:{v}' for (k,v) in headers.items()])
        


class PyCurlResponse(Response):
    def __init__(self, status:int = 500, data:Any = {}) -> None:
        self._status = status
        self._data = data
        self._headers = {}
    
    def set_status(self, status:int):
        self._status = status
        
    @property
    def status(self) -> int:
        return self._status
    
    def set_data(self, data:Any):
        self._data = data
    
    def get_data(self) -> Any:
         return Json.loads(self._data) 
    
    def get_headers(self) -> Any:
        return self._headers.copy()
    
    def put_header(self, head_line:bytes):
        if (line := head_line.decode()).find(":") > 0:
                key , val = line.split(':', 1)
                self._headers[key.strip()] = val.strip()
        
        
    