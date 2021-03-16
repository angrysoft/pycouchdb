#!/usr/bin/python

import json
import argparse
from typing import Dict, Any
from pycouchdb.client import Client

class Opts:
    pass

class RestoreAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super().__init__(option_strings, dest, **kwargs)
        
    def __call__(self, parser, namespace, values, option_string=None):
        print('%r %r %r' % (namespace, values, option_string))
        setattr(namespace, self.dest, values)
    

class DumpAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        print(option_strings, dest, kwargs)
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super().__init__(option_strings, dest, **kwargs)
        
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        print(f'Dump database: {values} to file {values}.json')
        print(namespace.url)
        # cli = Client(url)
        # _data: Dict[str, Any] = {db_name: []}
        # db = cli.get_db(db_name)
        # for doc in db:
        #     del doc['_rev']
        #     _data[db_name].append(doc)
        
        # with open(f'{db_name}.json', 'w') as jfile:
        #     json.dump(_data, jfile)

def load(db_name:str, url:str):
    cli = Client(url)
    with open(f'{db_name}.json', 'r') as jfile:
        db_data = json.load(jfile)
        if db_name in cli:
            cli.delete(db_name)
        cli.create(db_name)
        db = cli.get_db(db_name)
        print(f'Restoring {db_name}')
        for doc in db_data[db_name]:
            db.add(doc)

def dump(db_name:str, url:str):
    print(f'Dump database: {db_name} to file {db_name}.json')
    cli = Client(url)
    _data: Dict[str, Any] = {db_name: []}
    db = cli.get_db(db_name)
    for doc in db:
        del doc['_rev']
        _data[db_name].append(doc)
        
    with open(f'{db_name}.json', 'w') as jfile:
        json.dump(_data, jfile)

if __name__ == "__main__":
    opt = Opts()
    parser = argparse.ArgumentParser(usage='%(prog)s [options] [packages]')
    # parser.add_argument('dbs', nargs='*')
    parser.add_argument('-u', '--url', help='url sever')
    parser.add_argument('-d', '--dump', action=DumpAction, help="Dump database to json file")
    parser.add_argument('-r', '--restore', action=RestoreAction, help="Restore database from json file")
    
    args = parser.parse_args()
    print(args)