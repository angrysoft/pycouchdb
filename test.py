#!/usr/bin/python3
import unittest
from pycouchdb import Server


class PyCouchdbTest(unittest.TestCase):
    def setUp(self):
        self.s = Server()
        self.db = self.s.db('users')

    def test_server_inof(self):
        print(f'Server info : {self.s.version}, {self.s.uuid}, {self.s.vendor}')

    def test_db_info(self):
        print(f"db info : {self.s.db('users')}")

    def test_list_dbs(self):
        print('DB list')
        for db in self.s:
            print(f'db name = {db}')

    def test_all_dbs(self):
        print(f'all dbs {self.s.all_dbs()}')

    def test_all_docs(self):
        print(f'all docs : {self.db.all_doc()}')

    def test_list_docs(self):
        print('doc list')
        for doc in self.db:
            print(doc)

    def test_check(self):
        if 'damian.kozłowski@ves.pl' in self.db:
            print('jest')

    def test_get_item(self):
        print(f"get item : {self.db['sebastian.zwierzchowski@ves.pl']}")
        print(f"get item : {self.db['damian.kozłowski@ves.pl']}")


if __name__ == '__main__':
    unittest.main()
