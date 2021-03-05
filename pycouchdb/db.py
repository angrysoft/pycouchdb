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

from .doc import Document
from typing import Any, Dict
from .connections import Connection
from .exceptions import DatabaseError

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

    def get(self, docid:str, attchments:bool=False, att_encoding_info=False, atts_since=[], conflicts=False, deleted_conflicts=False, latest=False):
        """
            Get docmument by id
            
            Args:
                docid (str): Document ID
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
        
        _query = {}
        
        if attchments:
            headers = {'Accept': 'multipart/related',
                       'Accept': 'multipart/mixed'}
            _query['attachments'] =  'true'
        
        if att_encoding_info:
            _query['att_encoding_info'] = 'true'
        
        
        resp = self.conn.get(f'{self.name}/{docid}', query=_query)
        if resp.status in (200, 304):
            return resp.get_data()
        elif resp.status == 400:
            raise DatabaseError(messeage='The format of the request or revision was invalid')
        elif resp.status == 404:
            # raise DatabaseError('Specified database or document ID doesn’t exists')
            return {}
        else:
            raise DatabaseError(resp.status)

    def add(self, doc, batch=False):
        """
            Creates a new document in database
            
            Args:
                doc (dict): Document ID. 
                batch (bool): Stores document in batch mode
             
            Returns:
                tuple: document id, revision
            
            Raises:
                DatabaseError
            
            You can write documents to the database at a higher rate by using the 
            batch option. This collects document writes together in memory
            (on a per-user basis) before they are committed to disk.
            This increases the risk of the documents not being stored in 
            the event of a failure, since the documents are not written 
            to disk immediately.
        """
        
        if '_id' in doc:
            if type(doc['_id']) is not str:
                doc['_id'] = str(doc['_id'])

        _query = {}
        if batch:
            _query['batch'] = 'ok'
        resp = self.conn.post(path=self.name, data=doc, query=_query)
        if resp.status in (201, 202):
            ret = resp.get_data()
            return ret.get('id'), ret.get('rev')
        else:
            raise DatabaseError(resp.status)

    def update(self, docid:str, doc: Dict[str, Any]):
        _doc = self.get(docid)
        _doc.update(doc)
        resp = self.conn.put(path=f'{self.name}/{docid}', data=_doc, query={'rev': _doc.get('_rev')})
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

    def delete(self, doc_id:str):
        """Marks the specified document as deleted
        
        Args:
            docid (str): Document ID
        
        Return:
            tuple: document id rev
        
        Raises:
            DatabaseError
        """
        info = self.doc_info(doc_id)
        resp = self.conn.delete(path=f'{self.name}/{doc_id}', query={'rev': info.get('rev')})
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

    def all_docs(self, *keys):
        path = f'{self.name}/_all_docs'
        _keys = list()
        _keys.extend(keys)
        if keys:
            resp = self.conn.post(path, data={"keys": _keys})
        else:
            resp = self.conn.get(path)
        return resp.get_data()
    
    def get_all_docs(self):
        doc = self.all_docs()
        rows = doc.get('rows')
        i = 0
        while i <= (len(rows)-1):
            doc = rows[i]
            i += 1
            yield Document.from_dict(self.get(doc['id']), self)

    def find(self, selector={}, fields=[], sort=[], limit=25, skip=0, execution_status=False):
        query = {
            'selector': selector,
        }
        if fields:
            query['fileds'] = fields
        
        if sort:
            query['sort'] = sort
        
        query['limit'] = limit # defautl 25
        
        if skip:
            query['skip'] = skip
        
        if execution_status:
            query['execution_status'] = True
            
        path = f'{self.name}/_find'
        resp = self.conn.post(path=path, data=query)
        if resp.status == 200:
            return resp.get_data()
        elif resp.status == 400:
            raise DatabaseError(messeage='Invalid request')
        else:
            raise DatabaseError(resp.status)
    
    def bulk_add(self, docs_list):
        if type(docs_list) is not list:
            raise ValueError(f'args List expected not {type(docs_list)}')
            
        docs = {'docs': docs_list}
        
        # for doc in docs:
        #     if isinstance(doc, Document):
        #         docs['docs'].append()
        #     elif type(doc) == dict:
        #         docs['docs'].append(doc)
        path = f'{self.name}/_bulk_docs'
        resp = self.conn.post(path=path, data=docs)
        if resp.status == 201:
            return resp.get_data()
        elif resp.status == 400:
            raise DatabaseError(messeage='The request provided invalid JSON data')
        else:
            raise DatabaseError(resp.status)
        
    
    def bulk_get(self, id_list):
        if type(id_list) is not list:
            raise ValueError(f'args List expected not {type(id_list)}')
        docs = {'docs': list()}
        for _id in id_list:
            if type(_id) == dict:
                docs['docs'].append(_id)
            elif type(_id) == str:
                docs['docs'].append({'id': _id})
                
        path = f'{self.name}/_bulk_get'
        resp = self.conn.post(path=path, data=docs)
        if resp.status == 200:
            ret = resp.get_data()
            _dosc_list = list()
            if type(ret) is dict:
                return ret.get('results', list())
            else:
                return list()
        elif resp.status == 400:
            raise DatabaseError(messeage='The request provided invalid JSON data or invalid query parameter')
        else:
            raise DatabaseError(resp.status)
    
    def bulk_update(self, docs_list):
        if type(docs_list) is not list:
            raise ValueError(f'args List expected not {type(docs_list)}')
        
        for doc in docs_list:
            if '_id' not in doc:
                raise ValueError('Missing id in doc')
        
        docs = {'docs': docs_list}
        path = f'{self.name}/_bulk_docs'
        resp = self.conn.post(path=path, data=docs)
        if resp.status == 201:
            return resp.get_data()
        elif resp.status == 400:
            raise DatabaseError(messeage='The request provided invalid JSON data')
        else:
            raise DatabaseError(resp.status)
        

    # def purge(self, docinfo):
    #     resp = self.conn.post(path=f'{self.name}/_purge')
    #     if resp.status in (201, 202):
    #         ret = resp.get_data()
    #         return ret.get('id'), ret.get('rev')
    #     elif resp.status == 400:
    #         raise DatabaseError('Bad Request – Invalid database name')
    #     elif resp.status == 500:
    #         raise DatabaseError('Internal server error or timeout')

    def __contains__(self, item):
        resp = self.conn.head(path=f'{self.name}/{item}')
        if resp.status in (200, 304):
            return True
        elif resp.status == 404:
            return False
        else:
            raise DatabaseError(resp.status)

    def __iter__(self):
        doc = self.all_docs()
        self.rows = doc.get('rows')
        self.i = 0
        return self

    def __next__(self):
        if self.i <= (len(self.rows)-1):
            doc = self.rows[self.i]
            self.i += 1
            return doc['id']
        else:
            raise StopIteration

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        if key in self:
            self.update(key, value)
        else:
            value['_id'] = key
            self.add(value)
