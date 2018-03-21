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
    :type index_client: indexclient.client.IndexClient
    """
    hashes = {'md5': 'ab167e49d25b488939b1ede42752458c'}
    doc = index_client.create(
        hashes=hashes,
        size=10,
        file_name="removable.txt",
        urls=["google.com"]
    )
    latest = index_client.get_latest_revision(doc.did)
    assert latest.did == doc.did
    assert latest.file_name == doc.file_name
    assert latest.hashes == doc.hashes


def test_invalid_input(index_client):
    """
    :type index_client: indexclient.client.IndexClient
    """

    with pytest.raises(HTTPError):
        index_client.get_latest_revision("AAA")
    with pytest.raises(TypeError):
        index_client.get_latest_revision(None)


def test_add_revision(index_client):
    """
    :type index_client: indexclient.client.IndexClient
    """

    hashes = {'md5': 'ab167e49d25b488939b1ede42752458c'}
    doc = index_client.create(
        hashes=hashes,
        size=1,
        urls=[]
    )

    doc.version = "1"
    rev_doc = index_client.add_revision(doc)
    assert rev_doc.did is not doc.did
    assert rev_doc.baseid == doc.baseid
    assert rev_doc.version == "1"

    latest = index_client.get_latest_revision(doc.did)
    assert latest.did == rev_doc.did
    assert latest.version == "1"


def test_auto_add_revision(index_client):
    """
    :type index_client: indexclient.client.IndexClient
    """
    hashes = {'md5': 'ab167e49d25b488939b1ede42752458c'}
    doc = index_client.create(
        hashes=hashes,
        size=12,
        file_name="brutalsheep.txt",
        urls=["tearloop.com"]
    )

    # add a revision
    doc.version = "1"
    rev_doc = index_client.add_revision(doc)
    assert rev_doc is not None

    # auto add revision
    rev_doc = index_client.auto_add_revision(doc.did)
    assert rev_doc is not None
    assert rev_doc.version == "2"
    assert rev_doc.did is not doc.did


def test_auto_add_revision_with_function(index_client):
    """
    :type index_client: indexclient.client.IndexClient
    """
    hashes = {'md5': 'ab167e49d25b488939b1ede42752458c'}
    doc = index_client.create(
        hashes=hashes,
        size=12,
        file_name="brutalsheep.txt",
        urls=["tearloop.com"]
    )

    # add a revision
    doc.version = "1"
    rev_doc = index_client.add_revision(doc)
    assert rev_doc is not None

    # auto add revision
    rev_doc = index_client\
        .auto_add_revision(doc.did, lambda x: str(int(x) + 4))
    assert rev_doc is not None
    assert rev_doc.version == "5"
    assert rev_doc.did is not doc.did


def test_list_versions(index_client):
    """
    :type index_client: indexclient.client.IndexClient
    """
    hashes = {'md5': 'ab167e49d25b488939b1ede42752458c'}
    doc = index_client.create(
        hashes=hashes,
        size=12,
        file_name="brutalsheep.txt",
        urls=["tearloop.com"]
    )

    # add a revision
    doc.version = "1"
    rev_doc = index_client.add_revision(doc)
    assert rev_doc is not None

    # list versions
    versions = index_client.list_versions(doc.did)

    assert len(versions) == 2
