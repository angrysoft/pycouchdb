#!/usr/bin/python3
from pycouchdb import Server, DatabaseError


class PyCouchdbTest():
    def __init__(self):
        self.s = Server()
        if 'testdb' in self.s:
            self.s.delete('testdb')
        self.s.create('testdb')
        self.db = self.s['testdb']
        self.db['db_info'] = {'info': "temporary test db", 'name': 'testdb'}
        print('doc info', self.db.doc_info('db_info'))
        self.docs = [{'number': 1, 'name': 'one', 'type': 'number'},
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

    def test_b_db_info(self):
        print(f"db info : {self.s.db('testdb')}")

    def test_c_db_add(self):
        for i, d in enumerate(self.docs):
            d['_id'] = i
            self.db.add(d)
            print(f'add {d}')

    def test_c1_db_update(self):
        try:
            self.db.update('0', {'name': 'oneone'})
            self.db['1'] = {'name': 'twotwo'}
            self.db['123'] = {'name': 'notexists'}
        except DatabaseError as err:
            print(err)
        self.test_e_list_docs()

    def test_d_all_docs(self):
        print(f'all docs : {self.db.all_doc()}')

    def test_e_list_docs(self):
        print('doc list')
        for doc in self.db:
            print(doc)

    def test_f_del(self):
        for i, d in enumerate(self.docs):
            print(f'del doc {self.db.delete(i)}')

    def tearDown(self):
        self.s.delete('testdb')


if __name__ == '__main__':
    test = PyCouchdbTest()
    test.test_a_server_info()
    test.test_b_db_info()
    test.test_c_db_add()
    test.test_d_all_docs()
    test.test_e_list_docs()
    test.test_c1_db_update()
    test.test_f_del()
    # test.tearDown()
