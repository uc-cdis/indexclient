import json
import logging
import sys
import warnings

import requests

from indexclient import errors


def _remove_extra_hashes(hash_dict, hash_set):
    """Remove extra hashes from set, log errors"""
    logging.error("multiple incompatible hashes specified")

    for hash in hash_dict.items():
        hash_set.remove(hash)

    for hash, _ in hash_set:
        logging.error(f"multiple values specified for {hash}")

    return hash_set


def search_record(host, port, limit, start, size, hashes, **kwargs):
    """
    Finds records matching specified search criteria.
    """
    if size is not None and size < 0:
        raise ValueError("size must be non-negative")

    if limit is not None and limit < 0:
        raise ValueError("limit must be non-negative")

    hash_set = set((h, v) for h, v in hashes)
    hash_dict = {h: v for h, v in hash_set}

    if len(hash_dict) < len(hash_set):
        hash_set = _remove_extra_hashes(hash_dict, hash_set)

        raise ValueError("conflicting hashes provided")

    hashes = [":".join([h, v]) for h, v in hash_dict.items()]

    resource = f"http://{host}:{port}/index/"

    params = {"limit": limit, "start": start, "hash": hashes, "size": size}

    res = requests.get(resource, params=params)

    try:
        res.raise_for_status()
    except Exception as err:
        raise errors.BaseIndexError(res.status_code, res.text) from err

    try:
        doc = res.json()
    except ValueError as err:
        reason = json.dumps({"error": "invalid json payload returned"})
        raise errors.BaseIndexError(res.status_code, reason) from err

    sys.stdout.write(json.dumps(doc))


# DEPRECATED 11/2019 -- interacts with old `/alias/` endpoint.
# For creating aliases for indexd records, prefer using
# the `add_alias` function, which interacts with the new
# `/index/{GUID}/aliases` endpoint.
def search_names(host, port, limit, start, size, hashes, **kwargs):
    """
    Finds records matching specified search criteria.
    """
    warnings.warn(
        (
            "This function is deprecated. For creating aliases for indexd "
            "records, prefer using the `add_alias_for_did` function, which "
            "interacts with the new `/index/{GUID}/aliases` endpoint."
        ),
        DeprecationWarning,
    )
    if size is not None and size < 0:
        raise ValueError("size must be non-negative")

    if limit is not None and limit < 0:
        raise ValueError("limit must be non-negative")

    hash_set = set((h, v) for h, v in hashes)
    hash_dict = {h: v for h, v in hash_set}

    if len(hash_dict) < len(hash_set):
        hash_set = _remove_extra_hashes(hash_dict, hash_set)

        raise ValueError("conflicting hashes provided")

    hashes = [":".join([h, v]) for h, v in hash_dict.items()]

    resource = f"http://{host}:{port}/alias/"

    params = {"limit": limit, "start": start, "size": size, "hashes": hashes}

    res = requests.get(resource, params=params)

    try:
        res.raise_for_status()
    except Exception as err:
        raise errors.BaseIndexError(res.status_code, res.text) from err

    try:
        doc = res.json()
    except ValueError as err:
        reason = json.dumps({"error": "invalid json payload returned"})
        raise errors.BaseIndexError(res.status_code, reason) from err

    sys.stdout.write(json.dumps(doc))


def config(parser):
    """
    Configure the search command.
    """
    parser.set_defaults(func=search_record)

    parser.add_argument(
        "--names",
        action="store_const",
        const=search_names,
        dest="func",
        help="search names instead of records",
    )

    parser.add_argument(
        "--limit", default=None, type=int, help="limit on number of ids to retrieve"
    )

    parser.add_argument("--start", default=None, help="starting id or alias")

    parser.add_argument("--size", default=None, type=int, help="filter based on size")

    parser.add_argument(
        "--hash",
        nargs=2,
        metavar=("TYPE", "VALUE"),
        action="append",
        dest="hashes",
        default=[],
        help="filter based on hash values",
    )

    parser.add_argument(
        "--url", action="append", dest="urls", default=[], help="filter based on urls"
    )
