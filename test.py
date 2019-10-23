#!/usr/bin/python3
import unittest
from pycouchdb import Document
import json

doc = Document()
doc['dupa'] = 'blada'
print(doc)
print(json.dumps(doc))