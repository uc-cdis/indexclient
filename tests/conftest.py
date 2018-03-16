import pytest

from cdisutilstest.code.conftest import indexd_client, mock_server, indexd_server

@pytest.fixture(scope='function')
def index_client(indexd_client):
    return indexd_client