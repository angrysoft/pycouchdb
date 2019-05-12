#!/usr/bin/python3

from pycouchdb import Server

s = Server()
# print(s.version)
# print(s.uuid)
# print(s.vendor)
# print(s.all_dbs())
d = s.db('devices')
if '158d000200a020x' in d:
    print('jest')