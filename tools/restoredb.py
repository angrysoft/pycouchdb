#!/usr/bin/python

from pycouchdb import Server
import json
import argparse



def load(dbname):
    srv = Server()
    with open(f'{dbname}.json', 'r') as jfile:
        dbdata = json.load(jfile)
        if dbname in srv:
            srv.delete(dbname)
        srv.create(dbname)
        db = srv.db(dbname)
        print(f'Restoring {dbname}')
        for doc in dbdata[dbname]:
            db.add(doc)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage='%(prog)s [options] [packagees]')
    parser.add_argument('dbs', nargs='*')
    args = parser.parse_args()
    for dbname in args.dbs:
        load(dbname)