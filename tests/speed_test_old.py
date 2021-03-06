#!/usr/bin/python3
from couchdb import Server
import timeit


class PyCouchdbTest():
    def __init__(self):
        self.s = Server('http://admin:test@localhost:5984')
        if 'speedtestdb' in self.s:
            self.s.delete('speedtestdb')
        self.db = self.s.create('speedtestdb')
        # self.db = self.s['speedtestdb']
        self.doc = {'number': 1, 'name': 'one', 'type': 'number'}
        self._to = 500

    def test_c_db_add(self):
        for i in range(0, self._to):
            doc = {'_id': str(i), 'number': 1, 'name': 'one', 'type': 'number'}
            self.db.save(doc)
    
    def test_d_db_get(self):
        ret = list()
        for i in range(0, self._to+1):
            ret.append(self.db[str(i)])

    def test_f_del(self):
        for i in range(0, self._to):
            self.db.delete(str(i))

    def tearDown(self):
        self.s.delete('testdb')


if __name__ == '__main__':
    test = PyCouchdbTest()
    # import os
    # os.system('systemctl restart couchdb')
    # from time import sleep
    # sleep(1)
    add_t = timeit.timeit(test.test_c_db_add, number=1)
    get_t = timeit.timeit(test.test_d_db_get, number=1)
    del_t = timeit.timeit(test.test_f_del, number=1)
    print(f'Add {test._to} in : {add_t}')
    print(f'Get {test._to} in : {get_t}')
    # print(f'Del time : {del_t}')
