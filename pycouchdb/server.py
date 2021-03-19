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


from typing import Dict, List, Any
from .connections.urllibcon import UrllibConn
from .exceptions import ServerError
     

class Server:
    """The CouchDB server interface provides the basic interface to a CouchDB server
    for obtaining CouchDB information and getting and setting configuration information.
    """
    def __init__(self, url:str='http://localhost:5984'):
        """Server constructor
        Args:
            url (str): url to database server

        """
        self.conn = UrllibConn(url=url)

    def get_server_info(self) -> Dict[str, Any]:
        resp = self.conn.get()
        return resp.get_data()

    def active_tasks(self) -> List[Dict[str,Any]]:
        """List of running tasks, including the task type, name, status and process ID.
        The result is a JSON array of the currently running tasks,
        with each task being described with a single object.
        Depending on operation type set of response object fields might be different.

        Returns:
            List[Dict[str,Any]]:    changes_done (number) – Processed changes
                                    database (string) – Source database
                                    pid (string) – Process ID
                                    progress (number) – Current percentage progress
                                    started_on (number) – Task start time as unix timestamp
                                    status (string) – Task status message
                                    task (string) – Task name
                                    total_changes (number) – Total changes to process
                                    type (string) – Operation Type
                                    updated_on (number) – Unix timestamp of last operation update
        """
        resp = self.conn.get(path='_active_tasks')
        return resp.get_data()

    def list_database_names(self) -> List[str]:
        """Returns a list of all the databases in the CouchDB instance.
        """
        ret: List[str] = []
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

        

