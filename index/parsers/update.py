import sys
import json
import argparse

import requests

from index.errors import BaseIndexError


def update_record(host, port, did, rev, size, urls, hashes, **kwargs):
    '''
    Update a record.
    '''
    resource = 'http://{host}:{port}/index/{did}'.format(
        host=host,
        port=port,
        did=did,
    )

    params = {
        'rev': rev,
    }

    data = {
        'size': size,
        'urls': urls,
        'hashes': {h:v for h,v in hashes},
    }

    res = requests.put(resource, params=params, json=data)

    try: res.raise_for_status()
    except Exception as err:
        raise BaseIndexError(res.status_code, res.text)

    try: doc = res.json()
    except ValueError as err:
        reason = json.dumps({'error': 'invalid json payload returned'})
        raise BaseIndexError(res.status_code, reason)

    sys.stdout.write(json.dumps(doc))


def config(parser):
    '''
    Configure the update command.
    '''
    parser.set_defaults(func=update_record)

    parser.add_argument('did',
        help='document id',
    )

    parser.add_argument('rev',
        help='document revision',
    )

    parser.add_argument('--size',
        type=int,
        help='size in bytes',
    )

    parser.add_argument('--url',
        metavar='URL',
        action='append',
        dest='urls',
        default=[],
        help='known URLs associated with data',
    )

    parser.add_argument('--hash',
        nargs=2,
        metavar=('TYPE', 'VALUE'),
        action='append',
        dest='hashes',
        default=[],
        help='hash type and value',
    )
