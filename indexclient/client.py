from json import dumps as json_dumps
from urlparse import urljoin

import requests


def handle_error(resp):
    if 400 <= resp.status_code < 600:
        try:
            json = resp.json()
            resp.reason = json["error"]
        except:
            pass
        finally:
            resp.raise_for_status()


class IndexClient(object):

    def __init__(self, baseurl, version="v0", auth=None):
        self.auth = auth
        self.url = baseurl
        self.version = version
        self.check_status()



    def url_for(self, *path):
        return urljoin(self.url, "/".join(path))

    def check_status(self):
        """Check that the API we are trying to communicate with is online"""
        resp = requests.get(self.url + '/index')
        handle_error(resp)

    def get(self, did):
        """Return a document object corresponding to a single did"""
        try:
            self._get("index", did)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            else:
                raise e
        return Document(self, did)

    def list(self, limit=float("inf"), after=None, page_size=100):
        """ Returns a generator of document objects. """
        yielded = 0
        params = {"limit": page_size, "after": after}
        while True:
            resp = self._get("index", params=params)
            handle_error(resp)
            json = resp.json()
            if not json["ids"]:
                return
            for did in json["ids"]:
                if yielded < limit:
                    yield Document(self, did)
                    yielded += 1
                else:
                    return
            params["after"] = json["ids"][-1]

    def create(self, did=None, urls=[], hashes={}, size=None):
        json = {
            "urls": urls,
            "form": "object",
            "hashes": hashes,
            "size": size
        }
        if did:
            json["did"] = did
        resp = self._post("index/", headers={"content-type": "application/json"},
                          data=json_dumps(json), auth=self.auth)
        return Document(self, resp.json()["did"])

    def create_alias(
            self, record, rev=None, size=None, hashes={}, release=None,
            metastring=None, host_authorities=None, keeper_authority=None):
        data = json_dumps({
            'rev': rev,
            'size': size,
            'hashes': hashes,
            'release': release,
            'metastring': metastring,
            'host_authorities': host_authorities,
            'keeper_authority': keeper_authority,
        })
        url = '/alias/' + record
        headers = {'content-type': 'application/json'}
        resp = self._put(url, headers=headers, data=data, auth=self.auth)
        return Document(self, resp.json())

    def _get(self, *path, **kwargs):
        resp = requests.get(self.url_for(*path), **kwargs)
        handle_error(resp)
        return resp

    def _post(self, *path, **kwargs):
        resp = requests.post(self.url_for(*path), **kwargs)
        handle_error(resp)
        return resp

    def _put(self, *path, **kwargs):
        resp = requests.put(self.url_for(*path), **kwargs)
        handle_error(resp)
        return resp

    def _patch(self, *path, **kwargs):
        resp = requests.patch(self.url_for(*path), **kwargs)
        handle_error(resp)
        return resp

    def _delete(self, *path, **kwargs):
        resp = requests.delete(self.url_for(*path), **kwargs)
        handle_error(resp)
        return resp


class DocumentDeletedError(Exception):
    pass


class Document(object):

    def __init__(self, client, did):
        self.client = client
        self.did = did
        self.urls = None
        self.sha1 = None
        self._fetched = False
        self._deleted = False
        self.refresh()

    def _check_deleted(self):
        if self._deleted:
            raise DocumentDeletedError("document {} has been deleted".format(self.did))

    def _render(self, include_rev=False):
        self._check_deleted()
        if not self._fetched:
            raise RuntimeError("Document must be fetched from server with doc.refresh() before being rendered as json")
        json = {
            "urls": self.urls,
        }
        if self.sha1:
            json["sha1"] = self.sha1
        if include_rev:
            json["rev"] = self.rev
        return json

    def to_json(self, include_rev=True):
        json = self._render(include_rev=include_rev)
        json["did"] = self.did
        return json

    def refresh(self):
        """refresh the document contents from the server"""
        self._check_deleted()
        json = self.client._get("index", self.did).json()
        assert json["did"] == self.did
        self.urls = json["urls"]
        self.rev = json["rev"]
        if json.get("sha1"):
            self.sha1 = json["sha1"]
        self._fetched = True

    def patch(self):
        """Patch the current document contents
        to be the new contents on the server"""
        self._check_deleted()
        self.client._patch("did", self.did,
                           params={"rev": self.rev},
                           headers={"content-type": "application/json"},
                           data=json_dumps(self._render()))
        self.refresh()  # to sync new rev from server

    def delete(self):
        self._check_deleted()
        self.client._delete("did", self.did,
                            params={"rev": self.rev})
        self._deleted = True
