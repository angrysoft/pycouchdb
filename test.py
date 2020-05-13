#!/usr/bin/python3
# import unittest
# from pycouchdb import Document
# import json

# doc = Document()
# doc['dupa'] = 'blada'
# print(doc)
# print(doc.json)

from pycouchdb import Server
s = Server()
d = s.db('config')
for x in d.get_all_docs():
    print(x)
    
