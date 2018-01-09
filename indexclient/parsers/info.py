import sys
import json
import logging
import argparse

import requests

from indexclient import errors


def info(host, port, name, **kwargs):
    '''
    Retrieve info by name.
    '''
    resource = 'http://{host}:{port}/alias/{name}'.format(
        host=host,
        port=port,
        name=name,
    )

    res = requests.get(resource)

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
    Configure the info command.
    '''
    parser.set_defaults(func=info)

    parser.add_argument('name',
        help='name of information to retrieve',
    )
