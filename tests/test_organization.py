import pytest

from flask import g, session
from schedulerApp.db import get_db

def test_org_page(auth, client, app):
    auth.login()
    assert client.get('/1/org_page').status_code == 200

    response = client.get(
        '/99/org_page'
    )  
    assert response.headers['Location'] == 'http://localhost/'     

    auth.make_avail_request()

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM availability_request WHERE avail_request_name ='testAR'", 
        ).fetchone() is not None

@pytest.mark.parametrize(('avail_request_name', 'start_date', 'start_time', 'end_date', 'end_time', 'tz', 'message'),(
    ('', '1/1/2030', '1:30a', '1/1/2030', '2:00p', 'UTC', b"A name is required"),
    ('testAR', '', '1:30a', '1/1/2030', '2:00p', 'UTC', b"There was a problem with your start date input"),
    ('testAR','1/1/2030', '', '1/1/2030', '2:00p', 'UTC', b"There was a problem with your start time input"),
    ('testAR','1/1/2030', '1:30a', '', '2:00p', 'UTC', b"There was a problem with your end date input"),
    ('testAR','1/1/2030', '1:30a', '1/1/2030', '', 'UTC', b"There was a problem with your end time input"),
    ('testAR','1/1/2030', '1:30a', '1/1/2030', '2:00p', '', b"Timezone is required")
))
def test_org_page_validate_input(avail_request_name, start_date, start_time, end_date, end_time, tz, message, auth):
    auth.login()
    response = auth.make_avail_request(
        avail_request_name=avail_request_name,
        start_date=start_date,
        start_time=start_time,
        end_date=end_date,
        end_time=end_time,
        tz=tz
    )
    assert message in response.data

def test_avail_request(auth, client, app):
    auth.login()
    auth.make_avail_request()
    assert client.get('/1/avail_request').status_code == 200

    response = client.get(
        '/99/avail_request'
    )  
    assert response.headers['Location'] == 'http://localhost/'

    auth.add_avail_slot()

    response = client.get('/1/avail_request')

    assert b"Available from 1/1/2021 10:00AM until 1/1/2021 1:00PM" in response.data

    with app.app_context():
        db = get_db()
        assert db.execute(
            "SELECT * FROM availability_slot WHERE member_id = 1", 
        ).fetchone() is not None  

        assert db.execute(
            "SELECT * FROM member_request WHERE member_id = 1 AND answered = 1",
        ).fetchone() is not None

@pytest.mark.parametrize(('start_date', 'start_time', 'end_date', 'end_time', 'message'),(
    ('', '1:30a', '1/1/2030', '2:00p', b"There was a problem with your start date input"),
    ('1/1/2030', '', '1/1/2030', '2:00p', b"There was a problem with your start time input"),
    ('1/1/2030', '1:30a', '', '2:00p', b"There was a problem with your end date input"),
    ('1/1/2030', '1:30a', '1/1/2030', '', b"There was a problem with your end time input")
))
def test_avail_request_validate_input(start_date, start_time, end_date, end_time, message, auth):
    auth.login()
    auth.make_avail_request()
    response = auth.add_avail_slot(
        start_date=start_date,
        start_time=start_time,
        end_date=end_date,
        end_time=end_time,
    )
    assert message in response.data

def test_book(auth, client, app):
    auth.login()
    auth.make_avail_request()
    assert client.get('/1/book').status_code == 200

    response = client.get(
        '/99/book'
    )  
    assert response.headers['Location'] == 'http://localhost/' 

    auth.book()

    with app.app_context():
        db = get_db()
        assert db.execute(
            '''SELECT * FROM booked_date WHERE booked_date_name = 'testAR' ''',
        ).fetchone() is not None

        assert db.execute(
            '''
            SELECT availability_request.completed FROM availability_request 
            WHERE availability_request.avail_request_id = 1 
            ''',
        ).fetchone()[0] == 1


@pytest.mark.parametrize(('start_date', 'start_time', 'end_date', 'end_time', 'message'),(
    ('', '1:30a', '1/1/2030', '2:00p', b"There was a problem with your start date input"),
    ('1/1/2030', '', '1/1/2030', '2:00p', b"There was a problem with your start time input"),
    ('1/1/2030', '1:30a', '', '2:00p', b"There was a problem with your end date input"),
    ('1/1/2030', '1:30a', '1/1/2030', '', b"There was a problem with your end time input")
))
def test_book_validate_input(start_date, start_time, end_date, end_time, message, auth):
    auth.login()
    auth.make_avail_request()
    response = auth.book(
        start_date=start_date,
        start_time=start_time,
        end_date=end_date,
        end_time=end_time,
    )
    assert message in response.data