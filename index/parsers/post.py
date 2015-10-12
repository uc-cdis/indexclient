import sys
import json
import argparse

import requests

from index import errors


def post_record(hashes, urls, size, **kwargs):
    '''
    Post a new record.
    '''
    resource = 'http://localhost:8080/index/'

    data = {
        'hash': {h:v for h,v in hashes},
        'size': size,
        'urls': urls,
        'type': 'object',
    }

    res = requests.post(resource, json=data)

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
    Configure the post command.
    '''
    parser.set_defaults(func=post_record)

    parser.add_argument('alias',
        nargs='?',
        help='optional alias to assign',
    )

    parser.add_argument('--hash',
        required=True,
        nargs=2,
        metavar=('TYPE', 'VALUE'),
        action='append',
        dest='hashes',
        default=[],
        help='hash type and value',
    )

    parser.add_argument('--size',
        required=True,
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
