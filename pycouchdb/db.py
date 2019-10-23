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

class Query:
    class Selector:
        def __init__(self, filed):
            pass
    
    class Fields:
        pass

    class Sort:
        pass

    def __init__(self):
        self._selector = Selector
        self._selector = {}
        self._fileds = []
        self._sort = []


class Database:
    # TODO Attachments
    def __init__(self, name, server):
        self.server = server
        self.name = name

    def doc_info(self, docid):
        resp = self.server.session.head(path=f'{self.name}/{docid}')
        if resp.code in (200, 304):
            return {'rev': resp.headers.get('ETag', '').strip('"'),
                    'size': resp.headers.get('Content-Length'),
                    'date': resp.headers.get('Date')}
        elif resp.code == 401:
            raise DatabaseError('Unauthorized – Write privileges required')
        elif resp.code == 404:
            raise DatabaseError('Specified database or document ID doesn’t exists')
        else:
            return {}

    def get(self, _id, attchments=False):
        # TODO query options
        # attachments(boolean) – Includes attachments bodies in response.Default is false
        # att_encoding_info(boolean) – Includes encoding
        # information in attachment stubs if the particular attachment is compressed.Default is false.
        # atts_since(array) – Includes attachments only since specified revisions.Doesn’t includes attachments
        # for specified revisions.Optional
        # conflicts(boolean) – Includes information about conflicts in document.Default is false
        # deleted_conflicts(boolean) – Includes information about deleted conflicted revisions.Default is false
        # latest(boolean) – Forces retrieving latest “leaf” revision, no matter what rev was requested.Default is false
        # local_seq(boolean) – Includes last update sequence for the document.Default is false
        # meta(boolean) – Acts same as specifying all conflicts,
        #   deleted_conflicts and revs_info query parameters.Default is false
        # open_revs(array) – Retrieves documents of specified leaf revisions.Additionally,
        #   it accepts value as all to return all leaf revisions.Optional
        # rev(string) – Retrieves document of specified revision.Optional
        # revs(boolean) – Includes list of all known document revisions.Default is false
        # revs_info(boolean) – Includes detailed information for all known document revisions.Default is false

        if attchments:
            headers = {'Accept': 'multipart/related'}

        resp = self.server.session.get(f'{self.name}/{_id}')
        if resp.code in (200, 304):
            return resp.json
        elif resp.code == 400:
            raise DatabaseError('The format of the request or revision was invalid')
        elif resp.code == 401:
            raise DatabaseError('Read privilege required')
        elif resp.code == 404:
            raise DatabaseError('Specified database or document ID doesn’t exists')

    def add(self, doc, batch=False):
        if '_id' in doc:
            if type(doc['_id']) is not str:
                doc['_id'] = str(doc['_id'])

        _query = {}
        if batch:
            _query['batch'] = 'ok'
        resp = self.server.session.post(path=self.name, data=doc, query=_query)
        if resp.code in (201, 202):
            ret = resp.json
            return ret.get('id'), ret.get('rev')
        elif resp.code == 400:
            raise DatabaseError('Bad Request – Invalid database name')
        elif resp.code == 401:
            raise DatabaseError('Unauthorized – Write privileges required')
        elif resp.code == 404:
            raise DatabaseError('Not Found – Database doesn’t exist')
        elif resp.code == 409:
            raise DatabaseError('Conflict – A Conflicting Document with same ID already exists')

    def update(self, docid, doc):
        _doc = self.get(docid)
        _doc.update(doc)
        resp = self.server.session.put(path=f'{self.name}/{docid}', data=_doc, query={'rev': _doc.get('_rev')})
        if resp.code in (200, 202):
            ret = resp.json
            return ret.get('id'), ret.get('rev')
        elif resp.code == 400:
            raise DatabaseError('Invalid request body or parameters')
        elif resp.code == 401:
            raise DatabaseError('Unauthorized – Write privileges required')
        elif resp.code == 404:
            raise DatabaseError('Specified database or document ID doesn’t exists')
        elif resp.code == 409:
            raise DatabaseError('Specified revision is not the latest for target document')

    def delete(self, docid):
        info = self.doc_info(docid)
        resp = self.server.session.delete(path=f'{self.name}/{docid}', query={'rev': info.get('rev')})
        if resp.code in (200, 202):
            ret = resp.json
            return ret.get('id'), ret.get('rev')
        elif resp.code == 400:
            raise DatabaseError('Invalid request body or parameters')
        elif resp.code == 401:
            raise DatabaseError('Unauthorized – Write privileges required')
        elif resp.code == 404:
            raise DatabaseError('Specified database or document ID doesn’t exists')
        elif resp.code == 409:
            raise DatabaseError('Specified revision is not the latest for target document')

    def all_docs(self, *keys):
        path = f'{self.name}/_all_docs'
        _keys = list()
        _keys.extend(keys)
        if keys:
            resp = self.server.session.post(path, data={"keys": _keys})
        else:
            resp = self.server.session.get(path)
        return resp.json

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
        resp = self.server.session.post(path=path, data=query)
        if resp.code == 200:
            return resp.json
        elif resp.code == 401:
            raise DatabaseError('Read permission required')
        elif resp.code == 500:
            raise DatabaseError('Query execution error')
    
    def query(self):
        pass
    
    def bulk_add(self, *docs):
        docs = {'docs': list()}
        
        for doc in docs:
            if isinstance(doc, Document):
                docs['docs'].append()
            elif type(doc) == dict:
                docs['docs'].append(doc)
        
    
    def bulk_get(self, *ids):
        docs = {'docs': list()}
        for _id in ids:
            if type(_id) == dict:
                docs['docs'].append(_id)
            elif type(_id) == str:
                docs['docs'].append({'id': _id})
        path = f'{self.name}/_bulk_get'
        resp = self.server.session.post(path=path, data=docs)
        if resp.code == 200:
            print('bulk')
            return resp.json

    # def purge(self, docinfo):
    #     resp = self.server.session.post(path=f'{self.name}/_purge')
    #     if resp.code in (201, 202):
    #         ret = resp.json
    #         return ret.get('id'), ret.get('rev')
    #     elif resp.code == 400:
    #         raise DatabaseError('Bad Request – Invalid database name')
    #     elif resp.code == 500:
    #         raise DatabaseError('Internal server error or timeout')

    def __contains__(self, item):
        resp = self.server.session.head(path=f'{self.name}/{item}')
        if resp.code == 200:
            return True
        else:
            return False

    def __iter__(self):
        doc = self.all_docs()
        self.rows = doc.get('rows')
        self.i = 0
        return self

    def __next__(self):
        if self.i <= (len(self.rows)-1):
            doc = self.rows[self.i]
            self.i += 1
            return self[doc['id']]
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


class DatabaseError(Exception):
    def __init__(self, status, code=0):
        msg = {
            400: 'Invalid database name',
            401: 'CouchDB Server Administrator privileges required',
            412: 'Database already exists'
               }
        self.message = msg.get(status, f'Unknow Error: {status}')


class DocumentError(Exception):
    pass
