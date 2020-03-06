#!/usr/bin/python

from pycouchdb import Server
import json
import argparse

def dump(dbname):
    print(f'Dump {dbname} to file {dbname}.json')
    srv = Server()
    _data = {dbname: []}
    db = srv.db(dbname)
    for doc in db:
        del doc['_rev']
        _data[dbname].append(doc)
        
    with open(f'{dbname}.json', 'w') as jfile:
        json.dump(_data, jfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage='%(prog)s [options] [packagees]')
    parser.add_argument('dbs', nargs='*')
    args = parser.parse_args()
    for dbname in args.dbs:
        dump(dbname)