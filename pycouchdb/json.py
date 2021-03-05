try:
    import ujson as json
except ImportError:
    import json
from typing import Any


class Json:
    @staticmethod
    def loads(s:str) -> Any:
        return json.loads(s)
    
    @staticmethod
    def dumps(obj: Any) -> str:
        return json.dumps(obj)