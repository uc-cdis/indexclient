import pytest
from cdisutilstest.code.conftest import indexd_server, indexd_client  # pylint: disable=unused-import


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
