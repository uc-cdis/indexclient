import pytest

from cdisutilstest.code.indexd_fixture import indexd_server
from indexclient.client import IndexClient


@pytest.fixture
def index_client(indexd_server):
    yield IndexClient(
        baseurl=indexd_server.baseurl, auth=indexd_server.auth)
