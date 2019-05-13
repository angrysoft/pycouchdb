#!/usr/bin/python3

from pycouchdb import Server

s = Server()
# print(s.version)
# print(s.uuid)
# print(s.vendor)
for db in s:
    print(db)
print(s.all_dbs())

d = s.db('devices')
print(d.all_doc('rgb01'))
if '158d000200a020' in d:
    print('jest')
else:
    print('nima')
# print(d.find({'name': '...'}))
print(d.all_doc())
for doc in d:
    print(doc)
print(d.doc('rgb01'))
print(d['rgb01'])

db = s['config']