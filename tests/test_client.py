
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
        size = 1,
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
