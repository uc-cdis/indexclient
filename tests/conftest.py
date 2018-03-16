import pytest

from cdisutilstest.code.conftest import *

@pytest.fixture(scope='function')
def index_client(indexd_client):
    return indexd_client