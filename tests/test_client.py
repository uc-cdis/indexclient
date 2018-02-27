def test_instantiate(index_client):
    hashes = {'md5': 'ab167e49d25b488939b1ede42752458b'}
    doc = index_client.create(
        hashes=hashes,
        size=5,
        urls=[]
    )
    assert doc.size == 5
    assert doc.hashes == hashes
