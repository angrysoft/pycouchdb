from typing import Dict, Any, List


class FindQuery:
    def __init__(self) -> None:
        self.selector: Dict[str, Dict[str, Any]] = {}
        self.limit: int = 25
        self.skip: int = 0
        self.sort: List[Dict[Any, Any]] = []
        self.fields: List[str] = []
        self.use_index: List[str] = []
        self.r: int = 1
        self.bookmark: str = ''
        self.update: bool = False
        self.stable: bool = False
        self.stale: str = ''
        self.execution_status: bool = False

    def to_json(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = {}
        ret['selector'] = self.selector.copy()
        
        ret['limit'] = self.limit
        
        if self.skip:
            ret['skip'] = self.skip
        
        if self.sort:
            ret['sort'] = self.sort
            
        if self.fields:
            ret['fields'] = self.fields
        
        if self.use_index:
            ret['']
        
        return ret
    

class IndexQuery:
    def __init__(self) -> None:
        self.fields: List[str] = []
        self.name: str = ''
        self.type:str = 'json'
    
    def to_json(self) -> Dict[str, Any]:
        return {"index": {"fields": self.fields.copy()},
                "name": self.name,
                "type": self.type}