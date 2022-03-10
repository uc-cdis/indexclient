import pytest
import uuid

from indexclient.client import Document, recursive_sort, UrlMetadata


def create_document(
        did=None, hashes=None, size=None, file_name=None, acl=None,
        urls=None, urls_metadata=None):

    did = str(uuid.uuid4()) if did is None else did

    return Document(None, did, json={
        'hashes': hashes or {},
        'size': size or 1,
        'file_name': file_name or 'file.txt',
        'urls': urls or ['one', 'two', 'three'],
        'acl': acl or ['1', '2', '3'],
        'urls_metadata': urls_metadata or {
            'one': {'1': 'one'},
            'two': {'2': 'two'},
            'three': {'3': 'three'},
        },
    })


def test_equals():
    doc1 = create_document(did='11111111-1111-1111-1111-111111111111')
    doc2 = create_document(did='11111111-1111-1111-1111-111111111111')
    assert doc1 == doc2


def test_not_equals():
    doc1 = create_document(acl=['1', '2'])
    doc2 = create_document(acl=['2', '3'])
    assert doc1 != doc2


def test_greater_than_less_than():
    doc1 = create_document(did='11111111-1111-1111-1111-111111111111')
    doc2 = create_document(did='11111111-1111-1111-1111-111111111112')
    assert doc2 > doc1
    assert doc1 < doc2

    # reverse order docs
    docs = [
        create_document(did='11111111-1111-1111-1111-11111111111' + str(suffix))
        for suffix in range(10, 0, -1)
    ]
    # sorted() sorts it in order from lowest to highest did because of __lt__/__gt__
    did = sorted(docs)[0].did
    for doc in sorted(docs)[1:]:
        assert doc.did > did
        did = doc.did


@pytest.mark.parametrize('given, expected', [
    (1, 1),
    ('one', 'one'),
    ([1, 4, 3, 2], [1, 2, 3, 4]),
    ({'dict': [1, 4, 3, 2]}, {'dict': [1, 2, 3, 4]}),
    ({'one': {'two': [1, 4, 3, 2]}}, {'one': {'two': [1, 2, 3, 4]}}),
])
def test_recursive_sort(given, expected):
    assert recursive_sort(given) == expected


TEST_URL = "fake_cleversafe_url"
TEST_STATE = "test_state"
TEST_URL_TYPE = "cleversafe"
TEST_URL_METADATA = UrlMetadata(
    url=TEST_URL, type=TEST_URL_TYPE, state=TEST_STATE
)


def create_doc_with_url():
    doc = create_document(
        urls=[TEST_URL],
        urls_metadata={
            TEST_URL: {"state": TEST_STATE, "type": TEST_URL_TYPE}
        }
    )

    return doc


def test_get_url_metadata():
    doc = create_doc_with_url()
    assert doc.get_url_metadata_by_type(url_type=TEST_URL_TYPE) == TEST_URL_METADATA


def test_get_url_metadata_negative():
    doc = create_doc_with_url()
    assert doc.get_url_metadata_by_type(url_type="dummy") is None


def test_get_url_by_type():
    doc = create_doc_with_url()
    assert doc.get_url_by_url_type(url_type=TEST_URL_TYPE) == TEST_URL


def test_get_url_by_type_negative():
    doc = create_doc_with_url()
    assert doc.get_url_by_url_type(url_type="dummy") is None


def test_get_state_by_type():
    doc = create_doc_with_url()
    assert doc.get_state_by_url_type(url_type=TEST_URL_TYPE) == TEST_STATE


def test_get_state_by_type_negative():
    doc = create_doc_with_url()
    assert doc.get_state_by_url_type(url_type="dummy") is None


def test_get_state_by_type_missing_state():
    doc = create_document(
        urls=[TEST_URL],
        urls_metadata={TEST_URL: {"type": TEST_URL_TYPE}}
    )
    url_metadata = doc.get_url_metadata_by_type(url_type=TEST_URL_TYPE)
    assert url_metadata

    state = doc.get_state_by_url_type(url_type=TEST_URL_TYPE)
    assert state is None
