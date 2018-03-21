import pytest
from cdisutilstest.code.conftest import indexd_server
from indexclient.client import IndexClient


@pytest.fixture(scope='session')
def index_client(indexd_server):
    """
    Handles getting all the docs from an
    indexing endpoint. Currently this is changing from
    signpost to indexd, so we'll use just indexd_client now.
    I.E. test to a common interface this could be multiply our
    tests:
    https://docs.pytest.org/en/latest/fixture.html#parametrizing-fixtures
    """
    client = IndexClient(baseurl=indexd_server.baseurl, auth=indexd_server.auth)
    yield client
    for doc in client.list():
        doc.delete()
