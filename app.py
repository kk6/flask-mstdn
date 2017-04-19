# -*- coding: utf-8 -*-
import json
import secrets
from flask import Flask, render_template, redirect, request, session, url_for
from mstdn import Mstdn, OAuth2Handler

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

with open('app.json') as fp:
    client_keys = json.load(fp)
CLIENT_ID = client_keys['client_id']
CLIENT_SECRET = client_keys['client_secret']
REDIRECT_URL = client_keys['redirect_uri']
BASE_URL = 'https://pawoo.net'


def _get_oauth(scope=('read', 'write', 'follow')):
    return OAuth2Handler(CLIENT_ID, CLIENT_SECRET, BASE_URL,
                         scope=scope, redirect_uri=REDIRECT_URL)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/auth')
def auth():
    oauth = _get_oauth()
    url = oauth.get_authorization_url()[0]
    return redirect(url)


@app.route('/callback')
def callback():
    oauth = _get_oauth()
    code = request.args.get('code')
    token = oauth.fetch_token(code, file_path='token.json')
    session['token'] = token
    return redirect(url_for('home'))


@app.route('/home')
def home():
    token = session.get('token')
    mstdn = Mstdn(token)
    resp = mstdn.home_timeline()
    return render_template('home.html', statuses=resp.json())
