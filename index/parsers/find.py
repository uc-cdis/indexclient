import sys
import json
import logging
import argparse

import requests

from index import errors


def find_urls(host, port, limit, start, hashes, size, **kwargs):
    '''
    Retrieve a record by id.
    '''
    resource = 'http://{host}:{port}/urls/'.format(
        host=host,
        port=port,
    )

    hashes = [':'.join([h,v]) for h,v in hashes]

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


def config(parser):
    '''
    Configure the find command.
    '''
    parser.set_defaults(func=find_urls)

    parser.add_argument('-l', '--limit',
        default=None,
        type=int,
        help='limit number of urls returned',
    )

    parser.add_argument('-s', '--start',
        default=None,
        help='starting offset in urls returned',
    )

    parser.add_argument('-S', '--size',
        required=True,
        type=int,
        help='filter based on size',
    )

    parser.add_argument('-H', '--hash',
        nargs=2,
        metavar=('TYPE', 'VALUE'),
        action='append',
        dest='hashes',
        default=[],
        help='filter based on hash values',
    )
