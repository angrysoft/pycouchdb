#!/usr/bin/python

import json
import argparse
from typing import Dict, Any
from pycouchdb.client import Client


def load(db_name:str, client: Client):
    with open(f'{db_name}.json', 'r') as jfile:
        db_data = json.load(jfile)
        if db_name in client:
            client.delete(db_name)
        client.create(db_name)
        db = client.get_db(db_name)
        print(f'Restoring {db_name}')
        for doc in db_data[db_name]:
            db.add(doc)


def dump(db_name:str, client: Client):
    print(f'Dump database: {db_name} to file {db_name}.json')
    _data: Dict[str, Any] = {db_name: []}
    db = client.get_db(db_name)
    for doc_id in db:
        doc = db[doc_id]
        del doc['_rev']
        _data[db_name].append(doc)
    
    with open(f'{db_name}.json', 'w') as jfile:
        json.dump(_data, jfile, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage='%(prog)s [options] [packages]')
    parser.add_argument('dbs', nargs='*')
    parser.add_argument('-u', '--url', help='url sever')
    parser.add_argument('-d', '--dump', action="store_true", help="Dump database to json file")
    parser.add_argument('-r', '--restore', action="store_true", help="Restore database from json file")
    
    args = parser.parse_args()
    client = Client(args.url)
    if args.dump:
        for db_name in args.dbs:
            dump(db_name, client)
    elif args.restore:
        for db_name in args.dbs:
            load(db_name, client)