import sys
import json
import logging
import argparse

import requests

from index import errors


def delete_alias(**kwargs):
    print(kwargs)


def delete_record(**kwargs):
    print(kwargs)


def config(parser):
    '''
    Configure the delete command.
    '''
    parser.set_defaults(func=delete_alias)

    parser.add_argument('-r','--record',
        action='store_const',
        const=delete_record,
        dest='func',
        help='look up by record id directly',
    )

    parser.add_argument('alias',
        help='id or alias of record to delete',
    )
