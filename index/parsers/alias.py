import sys
import json
import argparse

import requests

from index import errors


def alias_record(alias, record, **kwargs):
    '''
    Alias a record.
    '''
    resource = 'http://localhost:8080/alias/{alias}'.format(alias=alias)

    params = {
        'record': record,
    }

    res = requests.put(resource, params=params)

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
    Configure the alias command.
    '''
    parser.set_defaults(func=alias_record)

    parser.add_argument('record',
        help='record id to alias',
    )

    parser.add_argument('alias',
        help='alias to assign',
    )
