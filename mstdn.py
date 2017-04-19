# -*- coding: utf-8 -*-
import json
from urllib.parse import urlunsplit, urljoin

import requests
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session


def register_app(client_name, host, redirect_uris='urn:ietf:wg:oauth:2.0:oob',
                 scopes='read write follow'):
    """Register application

    Usage:

        >>> d = register_app('myapp', host='pawoo.net')
        >>> d
        {'id': 1234, 'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob', 'client_id': '...', 'client_secret': '...'}

    """
    data = {
        'client_name': client_name,
        'redirect_uris': redirect_uris,
        'scopes': scopes,
    }
    resp = requests.post("https://{host}/api/v1/apps".format(host=host), data=data)
    resp.raise_for_status()
    return resp.json()


def fetch_token(client_id, client_secret, email, password, host, scope=('read', 'write', 'follow')):
    token_url = "https://{host}/oauth/token".format(host=host)
    client = LegacyApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url=token_url, username=email, password=password,
                              client_id=client_id, client_secret=client_secret, scope=scope)
    return token


class OAuth2Handler:

    def __init__(self, client_id, client_secret, base_url,
                 scope=('read', 'write', 'follow'),
                 redirect_uri='urn:ietf:wg:oauth:2.0:oob'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.redirect_uri = redirect_uri
        self.scope = scope
        self._oauth = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, scope=scope)

    def get_authorization_url(self):
        url = urljoin(self.base_url, '/oauth/authorize')
        authorization_url, state = self._oauth.authorization_url(url)
        return authorization_url, state

    def fetch_token(self, code, file_path=None):
        token_url = urljoin(self.base_url, '/oauth/token')
        token = self._oauth.fetch_token(token_url, authorization_response=code, client_id=self.client_id,
                                        client_secret=self.client_secret, code=code)
        if file_path:
            with open(file_path, 'w') as fp:
                json.dump(token, fp, indent=2, sort_keys=True)
        return token


class Mstdn:
    """Mastodon API

    Usage:

        >>> token = fetch_token(...)
        >>> mstdn = Mstdn(token)
        >>> mstdn.toot("テスト")

    """
    def __init__(self, token, scheme='https', host='pawoo.net'):
        self.scheme = scheme
        self.host = host
        self.session = requests.Session()
        self.session.headers.update({'Authorization': 'Bearer ' + token['access_token']})

    def _build_url(self, path):
        return urlunsplit([self.scheme, self.host, path, '', ''])

    def _request(self, method, url, params=None):
        resp = self.session.request(method, url)
        resp.raise_for_status()
        return resp

    def home_timeline(self):
        url = self._build_url('/api/v1/timelines/home')
        return self._request('get', url)

    def toot(self, status):
        url = self._build_url('/api/v1/statuses')
        return self._request('post', url, data={'status': status})
