import sys
import json
import argparse

import requests

from index import errors


def name_record(name, rev=None, size=None, hashes=None, release=None,
                metadata=None, hosts=None, keeper=None, **kwargs):
    '''
    Alias a record.
    '''
    resource = 'http://localhost:8080/alias/{name}'.format(name=name)

    params = {
        'rev': rev,
    }

    data = {
        'size': size,
        'hashes': None if hashes is None else {h:v for h,v in hashes},
        'release': release,
        'metadata': metadata,
        'host_authorities': [h for h in set(hosts)],
        'keeper_authority': keeper,
    }

    res = requests.put(resource, params=params, json=data)

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
    Configure the name command.
    '''
    parser.set_defaults(func=name_record)

    parser.add_argument('name',
        help='name to assign',
    )

    parser.add_argument('rev',
        nargs='?',
        help='revision of name',
    )

    parser.add_argument('--size',
        default=None,
        type=int,
        help='size of underlying data',
    )

    parser.add_argument('--hash',
        nargs=2,
        metavar=('TYPE', 'VALUE'),
        action='append',
        dest='hashes',
        default=None,
        help='hash type and value',
    )

    parser.add_argument('--release',
        choices=['public', 'private', 'controlled'],
        help='data release type',
    )

    parser.add_argument('--metadata',
        help='metadata string',
    )

    parser.add_argument('--host',
        action='append',
        dest='hosts',
        default=None,
        help='host authority',
    )

    parser.add_argument('--keeper',
        help='data keeper authority',
    )
