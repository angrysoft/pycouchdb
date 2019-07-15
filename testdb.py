#!/usr/bin/python3
import unittest
from pycouchdb import Server


class PyCouchdbTest():
    def __init__(self):
        self.s = Server()
        # self.s.create('testdb')
        self.db = self.s['testdb']

    def test_a_server_info(self):
        print(f'Server info : {self.s.version}, {self.s.uuid}, {self.s.vendor}')

    def test_b_db_info(self):
        print(f"db info : {self.s.db('testdb')}")

    def test_c_db_add(self):
        docs = [{'number': 1, 'name': 'one'},
                {'number': 2, 'name': 'two'},
                {'number': 3, 'name': 'three'},
                {'number': 4, 'name': 'four'},
                {'number': 5, 'name': 'five'}]
        for i, d in enumerate(docs):
            print(i )
            d['_id'] = i
            self.db.add(d)

    def test_d_all_docs(self):
        print(f'all docs : {self.db.all_doc()}')

    def test_e_list_docs(self):
        print('doc list')
        for doc in self.db:
            print(doc)
    #
    # def test_check(self):
    #     if 'damian.kozłowski@ves.pl' in self.db:
    #         print('jest')
    #
    # def test_get_item(self):
    #     print(f"get item : {self.db['sebastian.zwierzchowski@ves.pl']}")
    #     print(f"get item : {self.db['damian.kozłowski@ves.pl']}")

    def tearDown(self):
        self.s.delete('testdb')


if __name__ == '__main__':
    test = PyCouchdbTest()
    test.test_a_server_info()
    test.test_b_db_info()
    test.test_c_db_add()
    test.test_d_all_docs()
    test.test_e_list_docs()
    # test.tearDown()
