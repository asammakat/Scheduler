import pytest

from flask import g, session
from schedulerApp.db import get_db

def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():
        assert get_db().execute(
            "select * from member where username = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data

def test_register_org(client, app, auth):
    auth.login()
    assert client.get('/auth/register_org').status_code == 200
    response = client.post(
        '/auth/register_org', data={'org_name': 'a', 'password': 'a'}
    )  
    assert response.headers['Location'] == 'http://localhost/' 

    with app.app_context():
        assert get_db().execute(
            "select * from organization where org_name = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Organization name is required.'),
    ('a', '', b'Password is required.'),
    ('testOrg', 'test', b'testOrg is already registered.'),
))
def test_register_org_validate_input(client, username, password, message, auth):
    auth.login()
    response = client.post(
        '/auth/register_org',
        data={'org_name': username, 'password': password}
    )
    assert message in response.data

def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['member_id'] == 1
        assert g.member[1] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

def test_add_to_roster(client, app, auth):
    auth.login()
    response = auth.add_to_roster('testOrg1', 'test')
    print(response.headers)
    assert response.headers['Location'] == 'http://localhost/' 
    
    with app.app_context():
        assert get_db().execute('SELECT * FROM roster WHERE member_id = 1') is not None


@pytest.mark.parametrize(('org_name', 'password', 'message'), (
    ('b', 'test', b'This organization does not exist.'),
    ('testOrg', 'b', b'Incorrect password.'),
    ('testOrg', 'test', b'You are already in the organization.')
))
def test_add_to_roster_validate_input(auth, org_name, password, message):
    auth.login()
    response = auth.add_to_roster(org_name, password)
    assert message in response.data

@pytest.mark.parametrize('path', (
    '/1/org_page',
    '/auth/register_org',
    '/auth/add_to_roster',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'member_id' not in session
