from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any

class Connection(ABC):
    
    @abstractmethod
    def __init__(self, url:str) -> None:
        pass
    
    @abstractmethod
    def get(self, path:str='', query:Dict[str,Any]={}) -> Response:
        pass
    
    @abstractmethod
    def post(self, path:str='', data:Any=None, headers:Dict[str, str]={}, query:Dict[str, Any]={}) -> Response:
        pass
    
    @abstractmethod
    def put(self, path:str='', data:Any=None, headers:Dict[str, str]={}, query:Dict[str, Any]={}) -> Response:
        pass
    
    @abstractmethod
    def delete(self, path:str, query:Dict[str, Any]={}) -> Response:
        pass
    
    @abstractmethod
    def head(self, path:str, query:Dict[str, Any]={}) -> Response:
        pass
    
class Response(ABC):
    @property
    @abstractmethod
    def status(self) -> int:
        pass
    
    @abstractmethod
    def get_data(self) -> Any:
        pass
    
    @abstractmethod
    def get_headers(self) -> Any:
        pass

    
    
    