import pytest

from flask import g, session
from schedulerApp.db import get_db

def test_index(client):
    assert client.get('/').status_code == 200