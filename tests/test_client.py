import hashlib
import uuid

import pytest
from requests import HTTPError

from indexclient.client import Document


def test_instantiate(index_client):
    baseid = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
    urls = []
    size = 5
    acl = ['a', 'b']
    hashes = {'md5': 'ab167e49d25b488939b1ede42752458b'}
    doc = index_client.create(
        hashes=hashes,
        size=size,
        urls=urls,
        acl=acl,
        baseid=baseid,
    )
    assert doc.size == 5
    assert doc.hashes == hashes
    assert doc.size == size
    assert doc.urls == urls
    assert doc.baseid == baseid
    assert doc.acl == acl


def test_create_with_metadata(index_client):
    urls = ['s3://bucket/key']
    urls_metadata = {'s3://bucket/key': {'k': 'v'}}
    size = 5
    acl = ['a', 'b']
    hashes = {'md5': 'ab167e49d25b488939b1ede42752458b'}
    metadata = {'test': 'value'}
    doc = index_client.create(
        hashes=hashes,
        size=size,
        urls=urls,
        acl=acl,
        metadata=metadata,
        urls_metadata=urls_metadata,
    )
    assert doc.urls_metadata == urls_metadata
    assert doc.metadata == metadata


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


def create_test_index(index_client, version=None, current_did=None):
    """
        Shorthand for creating new index entries for test purposes
        Args:
            index_client (indexclient.client.IndexClient):
            version (str): version number of the index should be added
            current_did (str): if specifed add a version of the index with the did = current_did
        Returns:
            indexclient.client.Document: versioned document
        """

    did = str(uuid.uuid4())

    md5 = hashlib.md5()
    md5.update(did)
    # add a new node index
    hashes = {'md5': md5.hexdigest()}

    if current_did:
        data = {
            "size": 10,
            "hashes": hashes,
            "urls": [],
            "form": "object",
            "file_name": did + "_super_indexed_razzmatazz.xtx"
        }
        if version:
            data["version"] = version
        doc = index_client.add_version(current_did, Document(None, None, data))
    else:
        doc = index_client.create(
            hashes=hashes,
            size=5,
            version=version if version else "",
            file_name=did + "_super_indexed_razzmatazz.xtx",
            urls=[]
        )

    return doc


def test_get_latest_version_with_skip(index_client):
    """
    Args:
        index_client (indexclient.client.IndexClient): injected index client
    """
    doc = create_test_index(index_client, version="1")
    doc_2 = create_test_index(index_client, current_did=doc.did)

    v_doc = index_client.get_latest_version(doc_2.did, skip_null_versions=True)
    assert v_doc.did == doc.did
    assert v_doc.version == doc.version
    assert v_doc.baseid == doc_2.baseid


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

    data = {
        k: v for k, v in doc._doc.items()
        if k in ['size', 'hashes', 'form', 'urls']
    }
    data['version'] = '1'
    new_doc = Document(
        None, None, data
    )

    rev_doc = index_client.add_version(doc.did, new_doc)
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

    data = {
        k: v for k, v in doc._doc.items()
        if k in ['size', 'hashes', 'form', 'urls']
    }
    data['version'] = '1'
    new_doc = Document(
        None, None, data
    )
    rev_doc = index_client.add_version(doc.did, new_doc)
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
    doc.urls_metadata[doc.urls[0]] = {'a': 'b'}
    doc.patch()

    same_doc = index_client.get(doc.did)
    assert same_doc.metadata is not None
    assert same_doc.metadata.get("dummy_field", None) == "Dummy Var"
    assert same_doc.urls_metadata == {doc.urls[0]: {'a': 'b'}}


def test_updating_acl(index_client):
    """
    Args:
        index_client (indexclient.client.IndexClient): injected index client
    """
    hashes = {'md5': 'ab167e49d25b488939b1ede42752458c'}
    doc = index_client.create(
        hashes=hashes,
        size=12,
        urls=["s3://service.hidden.us/foundalsoinspace"]
    )

    doc.acl = ['a']
    doc.patch()

    same_doc = index_client.get(doc.did)
    assert same_doc.acl == ['a']
