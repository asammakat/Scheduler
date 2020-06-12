import os
import tempfile

import pytest
from schedulerApp import create_app
from schedulerApp.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )
    
    def add_to_roster(self, org_name='testOrg', password='test'):
        return self._client.post(
            'auth/add_to_roster',
            data={'org_name': org_name, 'password': password}
        )
    
    def make_avail_request(
        self, 
        org_id=1,
        avail_request_name='testAR', 
        start_date='1/1/2030', 
        start_time='1:30a', 
        end_date='1/1/2030', 
        end_time='2:00p', 
        tz='America/Los_Angeles'
    ):
        url = '/' + str(org_id) + '/org_page'
        return self._client.post(
            url,
            data={
                'avail_request_name': avail_request_name,
                'start_date': start_date, 
                'start_time': start_time,
                'end_date': end_date, 
                'end_time': end_time, 
                'tz': tz
            }
    )

    def add_avail_slot(
        self,
        avail_request_id = 1,      
        start_date='1/1/2030', 
        start_time='10:00a', 
        end_date='1/1/2030', 
        end_time='1:00p' 
    ):
        url = '/' + str(avail_request_id) + '/avail_request'
        return self._client.post(
            url,
            data={
                'start_date': start_date, 
                'start_time': start_time,
                'end_date': end_date, 
                'end_time': end_time, 
            }
        )
    
    def book(
        self, 
        start_date='1/1/2030', 
        start_time='10:00a', 
        end_date='1/1/2030', 
        end_time='1:00p'         
    ):
        return self._client.post(
            '/1/book',
            data={
                'start_date': start_date, 
                'start_time': start_time,
                'end_date': end_date, 
                'end_time': end_time, 
            }
        )

    def logout(self):
        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)