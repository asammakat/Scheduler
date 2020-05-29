import pytest

from flask import g, session
from schedulerApp.db import get_db

def test_org_page(auth, client):
    auth.login()
    assert client.get('/1/org_page').status_code == 200
    response = client.post(
        '/1/org_page'
    )  

