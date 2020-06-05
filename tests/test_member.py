import pytest

from flask import g, session
from schedulerApp.db import get_db

def test_index(client, auth, app):
    assert client.get('/').status_code == 200
    auth.login()
    auth.add_to_roster()
    auth.make_avail_request()
    t = client.get('/')
    print(t.data)
    assert b'**Respond**' in t.data
    auth.add_avail_slot()
    t = client.get('/')    
    assert b'**Respond**' not in t.data

