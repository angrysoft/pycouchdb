#!/usr/bin/python3
from pycouchdb import Server, DatabaseError
import timeit


class PyCouchdbTest():
    def __init__(self):
        self.s = Server()
        if 'speedtestdb' in self.s:
            self.s.delete('speedtestdb')
        self.s.create('speedtestdb')
        self.db = self.s['speedtestdb']
        self.doc = {'number': 1, 'name': 'one', 'type': 'number'}
        self._to = 500

    def test_c_db_add(self):
        for i in range(0, self._to):
            # self.doc['_id'] = i
            self.db[i] = self.doc

    def test_f_del(self):
        for i in range(0, self._to):
            self.db.delete(i)

    def tearDown(self):
        self.s.delete('testdb')


if __name__ == '__main__':
    test = PyCouchdbTest()
    print('restart')
    # import os
    # os.system('systemctl restart couchdb')
    # from time import sleep
    # sleep(1)
    add_t = timeit.timeit(test.test_c_db_add, number=1)
    # del_t = timeit.timeit(test.test_f_del, number=1)
    print(f'Add {test._to} in : {add_t}')
    # print(f'Del time : {del_t}')
    # test.tearDown()
