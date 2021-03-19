
from re import search
from .connections import Connection
from .connections.urllibcon import UrllibConn
from .db import Database
from .exceptions import ServerError
from typing import Callable, List


class Client:
    """Main class to connect to Database"""
    
    def __init__(self, url:str, connection_engine: Callable[[str], Connection] = UrllibConn) -> None:
        self.conn: Connection = connection_engine(url)
        
    def get_db(self, name:str):
        """Return database instance
        
        Args:
            name (str): Database name
        
        Returns:
            class: instance of pycouchdb.db.Database: 
        """
        
        if (resp := self.conn.head(path=name)).status == 200:
            return Database(name, self.conn)
        else:
            raise ServerError(resp.status)

    def create(self, db_name:str):
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
            dict:  status
        
        Raises:
            ServerError
            
        """
        db_name = db_name.lower()
        if not search('^[a-z][a-z0-9_$()+/-]*$', db_name):
            raise ValueError("Incorrect char in name")
        
        if (resp := self.conn.put(path=db_name)).status in (201, 202):
            return resp.get_data()
        else:
            raise ServerError(resp.status)

    def delete(self, db_name:str):
        """Deletes the specified database, and all the documents and attachments contained within it.
        
        Args:
            db_name (str): Database name
        
        Returns:
            dict:  status
        
        Raises:
            ServerError
        """
        
        if (resp := self.conn.delete(path=db_name)).status in (200, 202):
            return resp.get_data()
        else:
            raise ServerError(resp.status)
    
    def list_database_names(self) -> List[str]:
        """ List of all databases names
        
        Returns:
            list:   databases names
        """
        
        ret: List[str] = []
        if (resp := self.conn.get(path='_all_dbs')).status == 200:
            ret = resp.get_data().get('rows', [])
        return ret
     
    def __iter__(self):
        return iter(self.list_database_names())

    def __getitem__(self, db_name:str) -> Database:
        return self.get_db(db_name)

    def __contains__(self, item:str) -> bool:
        if self.conn.head(path=item).status == 200:
            return True
        else:
            return False
    
    def __repr__(self) -> str:
        return f'Client({self.list_database_names()})'