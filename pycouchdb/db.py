# Copyright 2019 - 2021 AngrySoft Sebastian Zwierzchowski
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
from __future__ import annotations
from .connections import Connection
from .exceptions import DatabaseError
from .query import FindQuery, IndexQuery
from typing import Any, Dict, List, Tuple

# TODO Attchement
class Database:
    
    def __init__(self, name:str, connection: Connection):
        """Class for db operations
        
        Args:
            name (str): Database name
            connection (Connection): instance of connection to server  
        """
        self.conn = connection
        self.name = name

    def doc_info(self, doc_id:str) -> Dict[str, Any]:
        """Minimal amount of information about the specified document.
           
            Args: 
                docid (str): Document ID.
                
            Returns:
                dict: Dictionary with keys rev - revision, size - size of document , date
            
            Raises:
                DatabaseError
        """
        
        if (resp := self.conn.head(path=f'{self.name}/{doc_id}')).status in (200, 304):
            return {'rev': resp.get_headers().get('ETag', '').strip('"'),
                    'size': resp.get_headers().get('Content-Length'),
                    'date': resp.get_headers().get('Date')}
        else:
            raise DatabaseError(resp.status)


    def add(self, doc:Dict[Any, Any]) -> Tuple[str, str]:
        """Creates a new document in database
            
            Args:
                doc (dict): Document ID. 
             
            Returns:
                tuple: document id, revision
            
            Raises:
                DatabaseError
            
        """
        
        if type(doc.get('_id', '')) is not str:
            raise DatabaseError("_id: need to be a str")

        if (resp := self.conn.post(path=self.name, data=doc)).status in (201, 202):
            ret = resp.get_data()
            return ret.get('id'), ret.get('rev')
        else:
            raise DatabaseError(resp.status)
    
    def add_batch(self, doc:Dict[Any, Any]):
        """write documents to the database at a higher rate by using the 
            batch option. This collects document writes together in memory
            (on a per-user basis) before they are committed to disk.
            This increases the risk of the documents not being stored in 
            the event of a failure, since the documents are not written 
            to disk immediately."""
            
        if (resp := self.conn.post(path=self.name, data=doc, query={'batch': 'ok'})).status in (201, 202):
            ret = resp.get_data()
            return ret
        else:
            raise DatabaseError(resp.status, messeage=f"Err {doc}")
    
    def add_many(self, docs: List[Dict[Any, Any]]):
        resp = self.conn.post(path=f'{self.name}/_bulk_docs', data={'docs': docs})
        if resp.status == 201:
            return resp.get_data()
        elif resp.status == 400:
            raise DatabaseError(messeage='The request provided invalid JSON data')
        else:
            raise DatabaseError(resp.status)
    
    def get(self, doc_id:str, attachments:bool=False, att_encoding_info:bool=False,
            atts_since:List[str]=[], conflicts:bool=False,
            deleted_conflicts:bool=False, latest:bool=False,
            rev: str = '', revs:bool = False) -> Dict[str, Any]:
        """
            Get document by id
            
            Args:
                doc_id (str): Document ID
                attachments (bool): Includes attachments bodies in response.Default is false
                att_encoding_info (bool): Includes encoding
            
            Returns: 
                Document
            
            Raises:
                DatabaseError
        """    
            # 
            #     information in attachment stubs if the particular attachment is compressed.Default is false.
            # atts_since(array) – Includes attachments only since specified revisions.Doesn’t includes attachments
            #     for specified revisions.Optional
            # conflicts(boolean) – Includes information about conflicts in document.Default is false
            # deleted_conflicts(boolean) – Includes information about deleted conflicted revisions.Default is false
            # latest(boolean) – Forces retrieving latest “leaf” revision, no matter what rev was requested.Default is false
            # local_seq(boolean) – Includes last update sequence for the document.Default is false
            # meta(boolean) – Acts same as specifying all conflicts,
            #     deleted_conflicts and revs_info query parameters.Default is false
            # open_revs(array) – Retrieves documents of specified leaf revisions.Additionally,
            #     it accepts value as all to return all leaf revisions.Optional
            # rev(string) – Retrieves document of specified revision.Optional
            # revs(boolean) – Includes list of all known document revisions.Default is false
            # revs_info(boolean) – Includes detailed information for all known document revisions.Default is false
        
        # TODO query options
        
        query: Dict[str, Any] = {}
        headers: Dict[str,str] = {}
        
        if attachments:
            headers.update({'Accept': 'application/json, multipart/related, multipart/mixed, text/plain'})
            query['attachments'] =  'true'
        
        if att_encoding_info:
            query['att_encoding_info'] = 'true'
        
        if rev:
            query['rev'] = rev
        
        
        resp = self.conn.get(f'{self.name}/{doc_id}', query=query)
        if resp.status in (200, 304):
            return resp.get_data()
        elif resp.status == 400:
            raise DatabaseError(messeage='The format of the request or revision was invalid')
        elif resp.status == 404:
            # Specified database or document ID doesn’t exists
            return {}
        else:
            raise DatabaseError(resp.status)
    
    def get_many(self,  ids: List[Dict[str, str]]) -> List[Dict[Any, Any]]:
        headers:Dict[str,str] = {'Accept': 'application/json, multipart/related, multipart/mixed'}
                
        resp = self.conn.post(path=f'{self.name}/_bulk_get', data={'docs': ids}, headers=headers)
        if resp.status == 200:
            ret = resp.get_data()
            return ret.get('results', [])
        elif resp.status == 400:
            raise DatabaseError(messeage='The request provided invalid JSON data or invalid query parameter')
        else:
            raise DatabaseError(resp.status)

    def update(self, doc_id:str, doc: Dict[str, Any], rev:str= '') -> Tuple[str, str]:
        headers = {'Content-Type': 'application/json, multipart/related'}
        _doc = self.get(doc_id, rev=rev)
        _doc.update(doc)
        
        query = {'rev': _doc.get('_rev')}
        
        resp = self.conn.put(path=f'{self.name}/{doc_id}',
                             data=_doc,
                             query=query,
                             headers=headers)
        if resp.status in (201, 202):
            ret = resp.get_data()
            return ret.get('id'), ret.get('rev')
        elif resp.status == 400:
            raise DatabaseError(messeage='Invalid request body or parameters')
        elif resp.status == 404:
            raise DatabaseError(messeage='Specified database or document ID doesn’t exists')
        elif resp.status == 409:
            raise DatabaseError(messeage='Specified revision is not the latest for target document')
        else:
            raise DatabaseError(resp.status)

    def update_many(self, docs_list: List[Dict[str, str]]):        
        resp = self.conn.post(path=f'{self.name}/_bulk_docs', data={'docs': docs_list})
        if resp.status == 201:
            return resp.get_data()
        elif resp.status == 400:
            raise DatabaseError(messeage='The request provided invalid JSON data')
        else:
            raise DatabaseError(resp.status)
    
    def delete(self, doc_id:str, rev:str='') -> Tuple[str, str]:
        """Marks the specified document as deleted
        
        Args:
            doc_id (str): Document ID
        
        Return:
            tuple: document id rev
        
        Raises:
            DatabaseError
        """
        query: Dict[str, Any] = {}
        
        if rev:
            query['rev'] = rev
        else:
            info = self.doc_info(doc_id)
            query={'rev': info.get('rev', '')}
            
        resp = self.conn.delete(path=f'{self.name}/{doc_id}', query=query)
        if resp.status in (200, 202):
            ret = resp.get_data()
            return ret.get('id'), ret.get('rev')
        elif resp.status == 400:
            raise DatabaseError(messeage='Invalid request body or parameters')
        elif resp.status == 404:
            raise DatabaseError(messeage='Specified database or document ID doesn’t exists')
        elif resp.status == 409:
            raise DatabaseError(messeage='Specified revision is not the latest for target document')
        else:
            raise DatabaseError(resp.status)
    
    def list_documents_names(self) -> List[Dict[str, Any]]:
        ret: List[Dict[str, Any]] = []
        if (resp := self.conn.get(path=f'{self.name}/_all_docs')).status == 200:
            ret = resp.get_data().get('rows', [])
        return ret
    
    def get_all(self):
        docs:List[Dict[str, Any]] = self.list_documents_names()
        for doc in docs:
            yield self.get(doc["id"])

    def find(self, query: FindQuery):
        resp = self.conn.post(path=f'{self.name}/_find', data=query.to_json())
        if resp.status == 200:
            return resp.get_data()
        elif resp.status == 400:
            raise DatabaseError(messeage='Invalid request')
        else:
            raise DatabaseError(resp.status)
    
    def set_index(self, index: IndexQuery) -> Dict[str,str]:
        resp = self.conn.post(path=f'{self.name}/_index', data=index.to_json())
        ret: Dict[str, str] = {}
        if resp.status == 200:
            ret = resp.get_data()
        elif resp.status >= 400:
            raise DatabaseError(code=resp.status)
        
        return ret
    
    def get_indexes(self) -> Dict[str, Any]:
        """Get a list of all indexes in the database.
        In addition to the information available through this API,
        indexes are also stored in design documents <index-functions>.
        Design documents are regular documents that have an ID starting with _design/.
        Design documents can be retrieved and modified in the same way as any other document,
        although this is not necessary when using Mango.
        
        Return:
            dict: total_rows (int) – Number of indexes
                  indexes (list) – Array of index definitions
        
        Raises:
            DatabaseError"""
        
        resp = self.conn.get(path=f'{self.name}/_index')
        
        ret: Dict[str, Any] = {}
        if resp.status == 200:
            ret = resp.get_data()
        elif resp.status >= 400:
            raise DatabaseError(code=resp.status)
        
        return ret
    
    def delete_index(self, design:str, name:str = '') -> Dict[str, bool]:
        """Delete index
        Args:
            design (str): Design Document ID starting with _design/
            name (str): Name of index 
        
        Return:
            dict: for example {"ok": true}
        
        Raises:
            DatabaseError"""
        
        resp = self.conn.delete(path=f"{self.name}/_index/{design}/json/{name}")
        ret: Dict[str, Any] = {}
        if resp.status == 200:
            ret = resp.get_data()
        elif resp.status >= 400:
            raise DatabaseError(code=resp.status)
        
        return ret    
    
    def purge(self, docinfo:Dict[str, List[str]]):
        """A database purge permanently removes the references to documents in the database.
        Normal deletion of a document within CouchDB does not remove the document from the database,
        instead, the document is marked as _deleted=true (and a new revision is created).
        This is to ensure that deleted documents can be replicated to other databases as having been deleted.
        This also means that you can check the status of a document and identify that the document has been deleted by its absence.
        The purge request must include the document IDs, and for each document ID, one or more revisions that must be purged.
        Documents can be previously deleted, but it is not necessary. Revisions must be leaf revisions.
        """
        
        resp = self.conn.post(path=f'{self.name}/_purge', data=docinfo)
        if resp.status in (201, 202):
            ret = resp.get_data()
            return ret.get('id'), ret.get('rev')
        elif resp.status == 400:
            raise DatabaseError('Bad Request – Invalid database name')
        elif resp.status == 500:
            raise DatabaseError('Internal server error or timeout')
    
    def get_design_docs(self):
        pass
    
    def __contains__(self, item:str):
        resp = self.conn.head(path=f'{self.name}/{item}')
        if resp.status in (200, 304):
            return True
        elif resp.status == 404:
            return False
        else:
            raise DatabaseError(resp.status)

    def __iter__(self):
        self.rows = self.list_documents_names()
        self.i = 0
        return self

    def __next__(self):
        if self.i <= (len(self.rows)-1):
            doc = self.rows[self.i]
            self.i += 1
            return doc['id']
        else:
            raise StopIteration

    def __getitem__(self, item:str):
        return self.get(item)

    def __setitem__(self, key:str, value: Any):
        if key in self:
            self.update(key, value)
        else:
            value['_id'] = key
            self.add(value)


        