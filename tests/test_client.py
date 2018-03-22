import pytest
from requests import HTTPError


def test_instantiate(index_client):
    hashes = {'md5': 'ab167e49d25b488939b1ede42752458b'}
    doc = index_client.create(
        hashes=hashes,
        size=5,
        urls=[]
    )
    assert doc.size == 5
    assert doc.hashes == hashes


def test_list_with_params(index_client):
    hashes = {'md5': 'ab167e49d25b488939b1ede42752458c'}
    doc = index_client.create(
        hashes=hashes,
        size=1,
        urls=[]
    )
    docs_with_hashes = index_client.list_with_params(
        params={'hashes': hashes}
    )
    found = False
    for d in docs_with_hashes:
        if d.did == doc.did:
            found = True
            break
    if not found:
        raise AssertionError()


def test_get_latest_revision(index_client):
    """
    Args:
        index_client (indexclient.client.IndexClient): injected index client
    """
    hashes = {'md5': 'ab167e49d25b488939b1ede42752458c'}
    doc = index_client.create(
        hashes=hashes,
        size=10,
        file_name="removable.txt",
        urls=["s3://service.hidden.us/lostinspace"]
    )
    latest = index_client.get_latest_version(doc.did)
    assert latest.did == doc.did
    assert latest.file_name == doc.file_name
    assert latest.hashes == doc.hashes


@pytest.mark.parametrize("arg, exception", [("AAA", HTTPError), (None, TypeError)])
def test_invalid_input(arg, exception, index_client):
    """
    Args:
        arg(str): uuid
        exception (Exception): Exception class
        index_client (indexclient.client.IndexClient): injected index client
    """

    with pytest.raises(exception):
        index_client.get_latest_version(arg)


def test_add_revision(index_client):
    """
    Args:
        index_client (indexclient.client.IndexClient): injected index client
    """

    hashes = {'md5': 'ab167e49d25b488939b1ede42752458c'}
    doc = index_client.create(
        hashes=hashes,
        size=1,
        urls=[]
    )

    doc.version = "1"
    rev_doc = index_client.add_version(doc.did, doc)
    assert rev_doc.did is not doc.did
    assert rev_doc.baseid == doc.baseid
    assert rev_doc.version == "1"

    latest = index_client.get_latest_version(doc.did)
    assert latest.did == rev_doc.did
    assert latest.version == "1"


def test_list_versions(index_client):
    """
    Args:
        index_client (indexclient.client.IndexClient): injected index client
    """
    hashes = {'md5': 'ab167e49d25b488939b1ede42752458c'}
    doc = index_client.create(
        hashes=hashes,
        size=12,
        file_name="brutalsheep.txt",
        urls=["s3://service.hidden.us/foundalsoinspace"]
    )

    # add a revision
    doc.version = "1"
    rev_doc = index_client.add_version(doc.did, doc)
    assert rev_doc is not None

    # list versions
    versions = index_client.list_versions(doc.did)

    assert len(versions) == 2
