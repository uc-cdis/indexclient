import pytest
from requests import HTTPError


def test_instantiate(index_client):
    baseid = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    urls = []
    size = 5
    hashes = {'md5': 'ab167e49d25b488939b1ede42752458b'}
    doc = index_client.create(
        hashes=hashes,
        size=size,
        urls=urls,
        baseid=baseid,
    )
    assert doc.size == 5
    assert doc.hashes == hashes
    assert doc.size == size
    assert doc.urls == urls
    assert doc.baseid == baseid


def test_list_with_params(index_client):
    hashes = {'md5': 'ab167e49d25b488939b1ede42752458c'}
    doc1 = index_client.create(
        hashes=hashes,
        size=1,
        urls=[]
    )
    doc2 = index_client.create(
        hashes=hashes,
        size=1,
        urls=[]
    )
    docs_with_hashes = index_client.list_with_params(
        page_size=1,
        params={'hashes': hashes}
    )
    dids = [doc1.did, doc2.did]
    found = []
    for d in docs_with_hashes:
        if d.did in dids:
            found.append(d.did)
    assert set(dids) == set(found)


def test_get_latest_version(index_client):
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


def test_add_version(index_client):
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

    # add a version
    doc.version = "1"
    rev_doc = index_client.add_version(doc.did, doc)
    assert rev_doc is not None

    # list versions
    versions = index_client.list_versions(doc.did)

    assert len(versions) == 2


def test_updating_metadata(index_client):
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

    doc.metadata["dummy_field"] = "Dummy Var"
    doc.patch()

    same_doc = index_client.get(doc.did)
    assert same_doc.metadata is not None
    assert same_doc.metadata.get("dummy_field", None) == "Dummy Var"
