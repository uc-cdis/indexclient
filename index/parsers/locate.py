import sys
import json
import logging
import argparse

import requests

from index import errors


def locate(*args, **kwargs):
    '''
    Gathers reported locations of data matching search criteria.
    '''
    pass


def config(parser):
    '''
    Configure the locate command.
    '''
    parser.set_defaults(func=locate)

    parser.add_argument('--limit',
        type=int,
        help='limit on number of ids to retrieve [100]',
    )

    parser.add_argument('--start',
        help='starting id or alias [""]',
    )

    parser.add_argument('--hash',
        required=True,
        nargs=2,
        metavar=('TYPE', 'VALUE'),
        action='append',
        dest='hashes',
        default=[],
        help='filter based on hash values',
    )

    parser.add_argument('size',
        type=int,
        help='filter based on file size',
    )
