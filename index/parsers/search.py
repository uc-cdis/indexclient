import sys
import json
import logging
import argparse

import requests

from index import errors


def search_record(limit=None, start=None, size=None, hashes=[], **kwargs):
    '''
    Finds records matching specified search criteria.
    '''
    hash_set = set((h,v) for h,v in hashes)
    hash_dict = {h:v for h,v in hash_set}

    if len(hash_dict) < len(hash_set):
        logging.error('multiple incompatible hashes specified')
        
        for h in hash_dict.items():
            hash_set.remove(h)
        
        for h, _ in hash_set:
            logging.error('multiple values specified for {h}'.format(h=h))
        
        raise ValueError('conflicting hashes provided')

    hashes = [':'.join([h,v]) for h,v in hash_dict.items()]

    resource = 'http://localhost:8080/index/'

    params = {
        'limit': limit,
        'start': start,
        'hash': hashes,
        'size': size,
    }

    res = requests.get(resource, params=params)

    try: res.raise_for_status()
    except Exception as err:
        raise errors.BaseIndexError(res.status_code, res.text)

    try: doc = res.json()
    except ValueError as err:
        reason = json.dumps({'error': 'invalid json payload returned'})
        raise errors.BaseIndexError(res.status_code, reason)

    sys.stdout.write(json.dumps(doc))


def search_alias(alias=None, limit=None, start=None, hashes=[], **kwargs):
    '''
    Find a alias record.
    '''
    alias = '' if alias is None else alias

    resource = 'http://localhost:8080/index/{alias}'.format(alias=alias)

    hash_set = set((h,v) for h,v in hashes)
    hash_dict = {h:v for h,v in hash_set}

    if len(hash_dict) < len(hash_set):
        logging.error('multiple incompatible hashes specified')
        
        for h in hash_dict.items():
            hash_set.remove(h)
        
        for h, _ in hash_set:
            logging.error('multiple values specified for {h}'.format(h=h))
        
        raise ValueError('conflicting hashes provided')

    hashes = [':'.join([h,v]) for h,v in hash_dict.items()]

    params = {
        'limit': limit,
        'start': start,
        'hash': hashes,
    }

    res = requests.get(resource, params=params)

    try: res.raise_for_status()
    except Exception as err:
        raise errors.BaseIndexError(res.status_code, res.text)

    try: doc = res.json()
    except ValueError as err:
        reason = json.dumps({'error': 'invalid json payload returned'})
        raise errors.BaseIndexError(res.status_code, reason)

    sys.stdout.write(json.dumps(doc))


def config(parser):
    '''
    Configure the search command.
    '''
    parser.set_defaults(func=search_alias)

    parser.add_argument('-r','--record',
        action='store_const',
        const=search_record,
        dest='func',
        help='look up by record id directly',
    )

    parser.add_argument('alias',
        nargs='?',
        help='id or alias of record to retrieve',
    )

    parser.add_argument('--limit',
        type=int,
        help='limit on number of ids to retrieve [100]',
    )

    parser.add_argument('--start',
        help='starting id or alias [""]',
    )

    parser.add_argument('--hash',
        nargs=2,
        metavar=('TYPE', 'VALUE'),
        action='append',
        dest='hashes',
        default=[],
        help='filter based on hash values',
    )
