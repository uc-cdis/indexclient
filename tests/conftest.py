import hashlib
import json

import pytest
from indexd_test_utils import (
    alias_driver,
    auth_driver,
    create_indexd_tables,
    index_driver,
    indexd_client,
    indexd_admin_user,
    indexd_server,
    setup_indexd_test_database,
)

from indexclient import client


@pytest.fixture(scope='function')
def index_client(indexd_client):
    """
    Handles getting all the docs from an
    indexing endpoint. Currently this is changing from
    signpost to indexd, so we'll use just indexd_client now.
    I.E. test to a common interface this could be multiply our
    tests:
    https://docs.pytest.org/en/latest/fixture.html#parametrizing-fixtures
    """
    return indexd_client


@pytest.fixture()
def indexd_loader(indexd_client):
    def load(file_name):
        docs = []  # type: list[client.Document]
        with open(file_name, "r") as f:
            doc_data = json.load(f)
        doc_data = doc_data["docs"]
        for doc in doc_data:

            # add dummy md5hash if no hash is specified
            if "hashes" not in doc:
                md5 = hashlib.md5()
                md5.update(doc["did"].encode("utf-8"))
                doc["hashes"] = {"md5": md5.hexdigest()}
            doc["urls"] = list(doc.get("urls_metadata", {}).keys())
            docs.append(indexd_client.create(**doc))
        return docs

    return load
