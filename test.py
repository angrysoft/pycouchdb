#!/usr/bin/python3

from pycouchdb import Server

s = Server()
print(s.version)
print(s.uuid)
print(s.vendor)
print(s.all_dbs())
d = s.db('users')

for db in s:
    print(db)
print(s.all_dbs())
if '158d000200a020' in d:
    print('jest')
else:
    print('nima')
# print(d.find({'name': '...'}))
print(d.all_doc())
# for doc in d:
#     print(doc)