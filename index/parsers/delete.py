import sys
import json
import logging
import argparse

import requests

from index.errors import BaseIndexError


def delete_record(did, rev, **kwargs):
    '''
    Create a new record.
    '''
    resource = 'http://localhost:8080/index/{did}'.format(did=did)

    params = {
        'rev': rev,
    }

    res = requests.delete(resource, params=params)

    try: res.raise_for_status()
    except Exception as err:
        raise BaseIndexError(res.status_code, res.text)

def config(parser):
    '''
    Configure the delete command.
    '''
    parser.set_defaults(func=delete_record)

    parser.add_argument('did',
        help='id or alias of record to delete',
    )

    parser.add_argument('rev',
        help='current revision of did',
    )
