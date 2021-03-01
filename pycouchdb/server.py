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

from re import search
from .db import Database
from typing import Dict, List, Any
from pycouchdb.connections.urllibcon import UrllibConn
     

class Server:
    """Main class to connect to Database
    
    Example:
        srv = Server()
        srv.create('userdb')
        users = srv.db('userdb')
        usr = {'name': 'john', 'lastname':'doe'}
        users.add(usr)
        srv.delete('usersdb')
    """
    
    def __init__(self, url:str='http://localhost', port:int=5984, user:str="", password:str="", ssl:bool=False):
        """Server constructor
        Args:
            url (str): url to database server
            port (int): port number for server connection default 5984
            user (str): user name 
            password (str): password
            ssl (bool): use https
        """
        self.conn = UrllibConn(url=url, port=port, user=user, password=password)
        self._version:str = ""
        self._uuid:str = ""
        self._vendor:str = ""
        self._get_server_info()

    @property
    def version(self) -> str:
        return self._version

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def vendor(self):
        return self._vendor

    def _get_server_info(self):
        resp = self.conn.get()
        ret = resp.get_data()
        self._version = ret.get('version', '')
        self._uuid = ret.get('uuid', '')
        self._vendor = ret.get('vendor', '')

    def active_tasks(self):
        resp = self.conn.get(path='_active_tasks')
        return resp.get_data()

    def all_dbs(self) -> List[str]:
        """Returns a list of all the databases in the CouchDB instance.
        """
        ret = []
        if (resp := self.conn.get(path='_all_dbs')).status == 200:
            ret = resp.get_data()
        return ret

    def dbs_info(self, *keys:str) -> List[Any]:
        """
        Returns information of a list of the specified databases in the CouchDB instance
        
        Args:
            keys (list): Array of database names to be requested
        
        Returns: 
            list: list of datebase info
        
        Raises:
            ServerError
        """
        
        if (resp := self.conn.post(path='_dbs_info', data={'keys': list(keys)})).status != 200:
            raise ServerError(resp.status)
        return resp.get_data()

    def get_cluster_setup(self) -> Dict[str, Any]:
        raise NotImplementedError
    
    def set_cluster_setup(self) -> None:
        raise NotImplementedError

    def db_updates(self, feed:str="", timeout:int=60, heartbeat:int=60000, since:str=""):
        args: Dict[str, Any] = dict()
        if feed:
            args['feed'] = feed
        if timeout:
            args['timeout'] = timeout
        if heartbeat:
            args['heartbeat'] = heartbeat
        if since:
            args['since'] = since
        if (resp := self.conn.get(path='_db_updates', query=args)).status != 200:
            raise ServerError(resp.status)
        return resp.get_data()

    def membership(self):
        """Displays the nodes that are part of the cluster as cluster_nodes.
        The field all_nodes displays all nodes this node knows about,
        including the ones that are part of the cluster.
        
        Returns:
            dict:
        """
        if (resp := self.conn.get(path='_membership')).status != 200:
            raise ServerError(resp.status)
        return resp.get_data()
    
    def set_replicate(self) -> Dict[str, Any]:
        raise NotImplementedError
    
    def is_up(self):
        """Confirms that the server is up, running, and ready to respond to requests."""
        
        if (resp := self.conn.get(path='_up')).status != 200:
            raise ServerError(resp.status)
        return resp.get_data()
    
    def db(self,name:str):
        Warning("Deprecated use get_db")
        return self.get_db(name)
    
    def get_db(self, name:str):
        """Return interface to database
        
        Args:
            name (str): Database name
        
        Returns:
            class: instance of pychouch.db.Database: 
        """
        
        if (resp := self.conn.head(path=name)).status == 200:
            return Database(name, self)
        else:
            raise ServerError(resp.status)

    def create(self, name:str):
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
        name = name.lower()
        if not search('^[a-z][a-z0-9_$()+/-]*$', name):
            raise ValueError("Incorrect char in name")
        
        if (resp := self.conn.put(path=name)).status in (201, 202):
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
        
    def __iter__(self):
        return iter(self.all_dbs())

    def __getitem__(self, item:str) -> Database:
        return self.db(item)

    def __contains__(self, item:str) -> bool:
        if self.conn.head(path=item).status == 200:
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
        

