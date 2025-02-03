import json
import sys

import requests

from indexclient.errors import BaseIndexError
from indexclient.parsers.utils import remove_extra_hashes


def update_record(host, port, did, rev, size, hashes, urls, **kwargs):
    """
    Update a record.
    """
    resource = f"http://{host}:{port}/index/{did}"

    params = {"rev": rev}

    if size < 0:
        raise ValueError("size must be non-negative")

    urls_set = set(urls)

    hash_set = set((h, v) for h, v in hashes)
    hash_dict = {h: v for h, v in hash_set}

    if len(hash_dict) < len(hash_set):
        hash_set = remove_extra_hashes(hash_dict, hash_set)
        raise ValueError("conflicting hashes provided")

    data = {"size": size, "urls": [u for u in urls_set], "hashes": hash_dict}

    res = requests.put(resource, params=params, json=data)

    try:
        res.raise_for_status()
    except Exception as err:
        raise BaseIndexError(res.status_code, res.text) from err

    try:
        doc = res.json()
    except ValueError as err:
        reason = json.dumps({"error": "invalid json payload returned"})
        raise BaseIndexError(res.status_code, reason) from err

    sys.stdout.write(json.dumps(doc))


def config(parser):
    """
    Configure the update command.
    """
    parser.set_defaults(func=update_record)

    parser.add_argument("did", help="document id")

    parser.add_argument("rev", help="document revision")

    parser.add_argument("--size", required=True, type=int, help="size in bytes")

    parser.add_argument(
        "--hash",
        required=True,
        nargs=2,
        metavar=("TYPE", "VALUE"),
        action="append",
        dest="hashes",
        help="hash type and value",
    )

    parser.add_argument(
        "--url",
        metavar="URL",
        action="append",
        dest="urls",
        default=[],
        help="known URLs associated with data",
    )
