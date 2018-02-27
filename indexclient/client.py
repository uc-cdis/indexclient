import json
from urlparse import urljoin

import requests


UPDATABLE_ATTRS = ['file_name', 'urls', 'version']


def json_dumps(data):
    return json.dumps({k: v for (k, v) in data.items() if v is not None})


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

    def url_for(self, *path):
        return urljoin(self.url, "/".join(path))

    def check_status(self):
        """Check that the API we are trying to communicate with is online"""
        resp = requests.get(self.url + '/index')
        handle_error(resp)

    def global_get(self, did, no_dist=False):
        """
        Makes a web request to the Indexd service global endpoint to retrieve
        an index document record.

        :param str did:
            The UUID for the index record we want to retrieve.

        :param boolean no_dist:
            *optional* Specify if we want distributed search or not

        :returns: A Document object representing the index record
        """
        try:
            if no_dist:
                response = self._get(did, params={'no_dist':''})
            else:
                response = self._get(did)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            else:
                raise e

        return Document(self, did, json=response.json())

    def get(self, did):
        """
        Makes a web request to the Indexd service to retrieve an index document record.

        :param str did:
            The UUID for the index record we want to retrieve.

        :returns: A Document object representing the index record
        """
        try:
            response = self._get("index", did)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            else:
                raise e

        return Document(self, did, json=response.json())

    def get_with_params(self, params=None):
        """
        Return a document object corresponding to the supplied parameters, such
        as ``{'hashes': {'md5': '...', 'size': '...'}}``.
        """
        try:
            response = self._get("index", params=params)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            else:
                raise e
        if not response.json()['ids']:
            return None
        did = response.json()['ids'][0]
        return Document(self, did)

    def list(self, limit=float("inf"), start=None, page_size=100):
        """ Returns a generator of document objects. """
        yielded = 0
        params = {"limit": page_size, "start": start}
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
            params["start"] = json['ids'][-1]

    def create(self, hashes, size, did=None, urls=None, file_name=None, metadata=None):
        if urls is None:
            urls = []
        json = {
            "urls": urls,
            "form": "object",
            "hashes": hashes,
            "size": size,
            "file_name": file_name,
            "metadata": metadata
        }
        if did:
            json["did"] = did
        resp = self._post(
            "index/", headers={"content-type": "application/json"},
            data=json_dumps(json), auth=self.auth)
        return Document(self, resp.json()["did"])

    def create_alias(
            self, record, size, hashes, release=None,
            metastring=None, host_authorities=None, keeper_authority=None):
        data = json_dumps({
            'size': size,
            'hashes': hashes,
            'release': release,
            'metastring': metastring,
            'host_authorities': host_authorities,
            'keeper_authority': keeper_authority
        })
        url = '/alias/' + record
        headers = {'content-type': 'application/json'}
        resp = self._put(url, headers=headers, data=data, auth=self.auth)
        return resp.json()

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

    def _delete(self, *path, **kwargs):
        resp = requests.delete(self.url_for(*path), **kwargs)
        handle_error(resp)
        return resp


class DocumentDeletedError(Exception):
    pass


class Document(object):

    def __init__(self, client, did, json=None):
        self.client = client
        self.did = did
        self._fetched = False
        self._deleted = False
        self._load(json)

    def _check_deleted(self):
        if self._deleted:
            raise DocumentDeletedError("document {} has been deleted".format(self.did))

    def _render(self, include_rev=True):
        self._check_deleted()
        if not self._fetched:
            raise RuntimeError("Document must be fetched from the server before being rendered as json")
        return self._doc

    def to_json(self, include_rev=True):
        json = self._render(include_rev=include_rev)
        json["did"] = self.did
        return json

    def _load(self, json=None):
        """ Load the document contents from the server or from the provided dictionary """
        self._check_deleted()
        json = json or self.client._get("index", self.did).json()
        # set attributes to current Document
        for k,v in json.iteritems():
            self.__dict__[k] = v
        self._attrs = json.keys()
        self._fetched = True

    def _doc_for_update(self):
        """
        return document with subset of attributes that are allowed
        to be updated
        """
        return {k:v for k,v in self._doc.items() if k in UPDATABLE_ATTRS}

    @property
    def _doc(self):
        return {k: self.__dict__[k] for k in self._attrs}


    def patch(self):
        """Patch the current document contents
        to be the new contents on the server"""
        self._check_deleted()
        self.client._put("/index", self.did,
                         params={"rev": self.rev},
                         headers={"content-type": "application/json"},
                         auth=self.client.auth,
                         data=json_dumps(self._doc_for_update()))
        self._load()  # to sync new rev from server

    def delete(self):
        self._check_deleted()
        self.client._delete("/index", self.did,
                            auth=self.client.auth,
                            params={"rev": self.rev})
        self._deleted = True
