#!/usr/bin/python3
import unittest
from pycouchdb import Server


class PyCouchdbTest(unittest.TestCase):
    def setUp(self):
        self.s = Server()
        self.db = self.s.db('users')

    def test_server_inof(self):
        print(f'{self.s.version}, {self.s.uuid}, {self.s.vendor}')

    def test_db_info(self):
        print(self.s.db('users'))

    def test_list_dbs(self):
        for db in self.s:
            print(f'db name = {db}')

    def test_all_dbs(self):
        print(self.s.all_dbs())

    def test_all_docs(self):
        print(self.db.all_doc())

    def test_list_docs(self):
        for doc in self.db:
            print(doc)


if __name__ == '__main__':
    unittest.main()
