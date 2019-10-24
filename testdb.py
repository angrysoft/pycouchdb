#!/usr/bin/python3
from pycouchdb import Server, DatabaseError
import unittest


class PyCouchdbTestSingle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Server(user='admin', password='admin')
        if 'testdb' in cls.s:
            print('remove testdb')
            cls.s.delete('testdb')
        print('create testdb')
        cls.s.create('testdb')
        print('db created')
        print('accesing db')
        cls.db = cls.s.db('testdb')
        
        cls.docs = [{'number': 1, 'name': 'one', 'type': 'number'},
                     {'number': 2, 'name': 'two', 'type': 'number'},
                     {'number': 3, 'name': 'three', 'type': 'number'},
                     {'number': 4, 'name': 'four', 'type': 'number'},
                     {'number': 5, 'name': 'five', 'type': 'number'},
                     {'letter': 'a', 'name': 'a', 'type': 'letter'},
                     {'letter': 'b', 'name': 'b', 'type': 'letter'},
                     {'letter': 'c', 'name': 'c', 'type': 'letter'},
                     {'letter': 'd', 'name': 'd', 'type': 'letter'},
                     {'letter': 'e', 'name': 'e', 'type': 'letter'}]

    def test_a_server_info(self):
        print(f'Server info : {self.s.version}, {self.s.uuid}, {self.s.vendor}')

    def test_c_db_add(self):
        print('\nAdding dosc:')
        for i, d in enumerate(self.docs):
            d['_id'] = i
            print(self.db.add(d))

    def test_d_db_update(self):
        print('\nUpdateing docs')
        try:
            self.db.update('0', {'name': 'oneone'})
            self.db['1'] = {'name': 'twotwo'}
            self.db['123'] = {'name': 'notexists'}
        except DatabaseError as err:
            print(err)
    
    def test_e_db_get(self):
        print(f"\nGet name from first doc: '{self.db['0']['name']}'")

    def test_ee_all_docs(self):
        print(f'\nGet all docs:\n{self.db.all_docs()}')

    def test_f_list_docs(self):
        print('\nGet doc in loop')
        for doc in self.db:
            print(doc)
    
    def test_g_find(self):
        print(f"\nFind: {self.db.find(selector={'type': 'number'})}")

    def test_h_del(self):
        print('\nDeleteing doc by id')
        for i, d in enumerate(self.docs):
            print(f'del doc {self.db.delete(i)}')

    @classmethod
    def tearDownClass(cls):
        cls.s.delete('testdb')


class PyCouchdbTestBulk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Server(user='admin', password='admin')
        if 'testdb' in cls.s:
            print('remove testdb')
            cls.s.delete('testdb')
        print('create testdb')
        cls.s.create('testdb')
        print('db created')
        print('accesing db')
        cls.db = cls.s.db('testdb')
        
        cls.docs = [{'_id':'0', 'number': 1, 'name': 'one', 'type': 'number'},
                    {'_id':'1', 'number': 2, 'name': 'two', 'type': 'number'},
                    {'_id':'2', 'number': 3, 'name': 'three', 'type': 'number'},
                    {'_id':'3', 'number': 4, 'name': 'four', 'type': 'number'},
                    {'_id':'4', 'number': 5, 'name': 'five', 'type': 'number'},
                    {'_id':'5', 'letter': 'a', 'name': 'a', 'type': 'letter'},
                    {'_id':'6', 'letter': 'b', 'name': 'b', 'type': 'letter'},
                    {'_id':'7', 'letter': 'c', 'name': 'c', 'type': 'letter'},
                    {'_id':'8', 'letter': 'd', 'name': 'd', 'type': 'letter'},
                    {'_id':'9', 'letter': 'e', 'name': 'e', 'type': 'letter'}]
    
    def test_a_bulk_add(self):
        print('\nBulk add docs')
        print(self.db.bulk_add(self.docs))
    
    def test_b_bulk_get(self):
         print('\nBulk get docs')
         print(self.db.bulk_get([str(x) for x in range(0,10)]))
    
    def test_c_bule_update(self):
        print('\nBulk update docs')
        docs = self.db.bulk_get([str(x) for x in range(0,10)])
        for i, x in enumerate(docs):
            print(i,x)
            
        # print(self.db.bulk_update(docs))
        
    def test_d_bulk_del(self):
        pass
        
if __name__ == '__main__':
    unittest.main()

