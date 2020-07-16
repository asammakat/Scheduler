import pytest

from flask import g, session
from schedulerApp.db import get_db

def test_org_page(auth, client, app):
    auth.login()
    auth.add_to_roster('testOrg1', 'test')
    auth.make_avail_request(org_id=2) 

    response = client.get('/2/org_page')
    assert response.status_code == 200
    assert b'testAR' in response.data
    assert b'Not completed' in response.data #no availability slots have been filled

    auth.add_avail_slot()
    auth.book()

    response = client.get('/2/org_page')
    assert response.status_code == 200
    assert b'testAR' in response.data
    assert b'Completed' in response.data #all availability slots have been filled
    assert b'from 1/1/2030 10:00AM ' in response.data #test time conversions
    assert b'until 1/1/2030 1:00PM' in response.data
    assert b'America/Los_Angeles' in response.data

    response = client.get(
        '/99/org_page'
    )  
    assert response.headers['Location'] == 'http://localhost/'     

    auth.make_avail_request()

    with app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM availability_request WHERE avail_request_name ='testAR'", 
        )
        result = cur.fetchone()
        assert result is not None

@pytest.mark.parametrize(('avail_request_name', 'start_date', 'start_time', 'end_date', 'end_time', 'tz', 'message'),(
    ('', '1/1/2030', '1:30a', '1/1/2030', '2:00p', 'UTC', b"A name is required"),
    ('testAR', '', '1:30a', '1/1/2030', '2:00p', 'UTC', b"There was a problem with your start date input"),
    ('testAR', '1/1/2030', '', '1/1/2030', '2:00p', 'UTC', b"There was a problem with your start time input"),
    ('testAR', '1/1/2030', '1:30a', '', '2:00p', 'UTC', b"There was a problem with your end date input"),
    ('testAR', '1/1/2030', '1:30a', '1/1/2030', '', 'UTC', b"There was a problem with your end time input"),
    ('testAR', '1/1/2030', '1:30a', '1/1/2030', '2:00p', '', b"Timezone is required"),
    ('testAR', '1/1/2030', '2:00p', '1/1/2030', '1:30a', 'UTC', b"Start must be before end")
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

    assert b"Available from 1/1/2030 10:00AM until 1/1/2030 1:00PM" in response.data
    assert b"Ready to book" not in response.data


    with app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM availability_slot WHERE member_id = 1", 
        )
        result = cur.fetchone()
        assert result is not None  

        cur.execute(
            "SELECT * FROM member_request WHERE member_id = 1 AND answered = TRUE",
        )
        result = cur.fetchone()
        assert result is not None

        cur.execute(
            '''
            SELECT * FROM availability_request WHERE completed = TRUE
            '''
        )
        result = cur.fetchone()
        assert result is None

        auth.add_to_roster('testOrg1', 'test')
        auth.make_avail_request(org_id=2)
        response = auth.add_avail_slot(avail_request_id=2)
        assert b"Ready to book" in response.data

        cur.execute(
            '''
            SELECT * FROM availability_request WHERE completed = TRUE
            '''
        )
        result = cur.fetchone()
        assert result is not None
        
@pytest.mark.parametrize(('start_date', 'start_time', 'end_date', 'end_time', 'message'),(
    ('', '1:30a', '1/1/2030', '2:00p', b"There was a problem with your start date input"),
    ('1/1/2030', '', '1/1/2030', '2:00p', b"There was a problem with your start time input"),
    ('1/1/2030', '1:30a', '', '2:00p', b"There was a problem with your end date input"),
    ('1/1/2030', '1:30a', '1/1/2030', '', b"There was a problem with your end time input"),
    ('1/1/2030', '2:00p', '1/1/2030', '1:30a', b"Start must be before end"),
    ('1/1/2019', '1:30a', '1/1/2030', '2:00p', b"availability slot cannot start before the availability request"),
    ('1/1/2030', '1:30a', '1/1/2050', '2:00p', b"avaiability slot cannot end after the availability request")

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
    auth.add_avail_slot()
    response = client.get('/1/book')

    assert response.status_code == 200
    assert b'testAR' in response.data
    assert b"Available from 1/1/2030 10:00AM until 1/1/2030 1:00PM" in response.data

    response = client.get(
        '/99/book'
    )  
    assert response.headers['Location'] == 'http://localhost/' 

    response = auth.book()
    assert response.headers['Location'] == 'http://localhost/?org_id=1'

    with app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute(
            '''SELECT * FROM booked_date WHERE booked_date_name = 'testAR' ''',
        )
        result = cur.fetchone()
        assert result is not None

@pytest.mark.parametrize(('start_date', 'start_time', 'end_date', 'end_time', 'message'),(
    ('', '1:30a', '1/1/2030', '2:00p', b"There was a problem with your start date input"),
    ('1/1/2030', '', '1/1/2030', '2:00p', b"There was a problem with your start time input"),
    ('1/1/2030', '1:30a', '', '2:00p', b"There was a problem with your end date input"),
    ('1/1/2030', '1:30a', '1/1/2030', '', b"There was a problem with your end time input"),
    ('1/1/2030', '2:00p', '1/1/2030', '1:30a', b"Start must be before end")
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

def test_delete_availability_request(auth, client, app):
    auth.login()
    auth.make_avail_request()
    assert client.get('/1/avail_request').status_code == 200

    with app.app_context():
        db = get_db()
        cur = db.cursor()     
        cur.execute(
            '''
            SELECT * 
            FROM availability_request 
            WHERE availability_request.avail_request_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is not None

        response = client.get('/1/delete_avail_request')
        assert response.headers['location'] == 'http://localhost/1/org_page'     

        cur.execute(
            '''
            SELECT * 
            FROM availability_request 
            WHERE availability_request.avail_request_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is None
    
def test_delete_avail_slot(auth, client, app):
    auth.login()
    auth.make_avail_request()
    auth.add_avail_slot()
    assert client.get('/1/avail_request').status_code == 200

    with app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute(
            '''
            SELECT * 
            FROM availability_slot
            WHERE availability_slot.avail_slot_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is not None

        request = client.get('/1/delete_avail_slot')

        # test for correct redirect
        assert request.headers['location'] == 'http://localhost/1/avail_request'

        # avail slot should not be deleted
        cur.execute(
            '''
            SELECT * 
            FROM availability_slot
            WHERE availability_slot.avail_slot_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is None        

def test_delete_booked_date(auth, client, app):
    auth.login()
    auth.make_avail_request()
    auth.book()
    assert client.get('/1/book').status_code == 200

    with app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute(
            '''
            SELECT * 
            FROM booked_date
            WHERE booked_date.booked_date_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is not None

        request = client.get('/1/delete_booked_date')
        assert request.headers['location'] == 'http://localhost/1/org_page'

        cur.execute(
            '''
            SELECT *
            FROM booked_date 
            WHERE booked_date.booked_date_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is None
    
def test_leave_org(auth, client, app):
    auth.login()
    auth.make_avail_request()
    auth.add_avail_slot()
    assert client.get('/').status_code == 200

    with app.app_context():
        db = get_db()
        cur = db.cursor()

        # make sure entries we expect are in the database are there
        cur.execute(
            '''
            SELECT * 
            FROM availability_slot
            WHERE availability_slot.avail_slot_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is not None

        cur.execute(
            '''
            SELECT * 
            FROM roster
            WHERE roster.org_id = 1
            AND roster.member_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is not None

        cur.execute(
            '''
            SELECT * 
            FROM member_request
            WHERE member_request.member_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is not None        

        # add an availability_slot that should not be deleted
        client.get('/logout')
        auth.login('other', 'test')
        auth.add_avail_slot()

        # make sure that new avail slot was added
        cur.execute(
            '''
            SELECT * 
            FROM availability_slot
            WHERE availability_slot.avail_slot_id = 2
            '''
        )
        result = cur.fetchone()
        assert result is not None        

        request = client.get('/1/1/leave_org')
        assert request.headers['location'] == 'http://localhost/'

        # this member should be deleted from the roster
        cur.execute(
            '''
            SELECT * 
            FROM roster
            WHERE roster.org_id = 1
            AND roster.member_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is None

        # other member in the org should not be deleted from roster
        cur.execute(
            '''
            SELECT * 
            FROM roster
            WHERE roster.org_id = 1
            AND roster.member_id = 2
            '''
        )
        result = cur.fetchone
        assert result is not None

        # availability slot associated with organization should also be deleted
        cur.execute(
            '''
            SELECT * 
            FROM availability_slot
            WHERE availability_slot.avail_slot_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is None

        # make sure member request associated with the member 
        # and the availability request has been deleted
        cur.execute(
            '''
            SELECT * 
            FROM member_request
            WHERE member_request.member_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is None

        # this availability slot should not be deleted
        cur.execute(
            '''
            SELECT * 
            FROM availability_slot
            WHERE availability_slot.avail_slot_id = 2
            '''
        )
        result = cur.fetchone()
        assert result is not None

        # this member_request should not be deleted
        cur.execute(
            '''
            SELECT * 
            FROM member_request
            WHERE member_request.member_id = 2
            '''
        )
        result = cur.fetchone()
        assert result is not None
    
def test_drop_from_org(auth, client, app):
    auth.login()
    auth.make_avail_request()
    auth.add_avail_slot()
    assert client.get('/').status_code == 200

    with app.app_context():
        db = get_db()
        cur = db.cursor()

        # make sure entries we expect are in the database are there
        cur.execute(
            '''
            SELECT * 
            FROM availability_slot
            WHERE availability_slot.avail_slot_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is not None

        cur.execute(
            '''
            SELECT * 
            FROM roster
            WHERE roster.org_id = 1
            AND roster.member_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is not None

        cur.execute(
            '''
            SELECT * 
            FROM member_request
            WHERE member_request.member_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is not None        

        # add an availability_slot that should not be deleted
        client.get('/logout')
        auth.login('other', 'test')
        auth.add_avail_slot()

        # make sure that new avail slot was added
        cur.execute(
            '''
            SELECT * 
            FROM availability_slot
            WHERE availability_slot.avail_slot_id = 2
            '''
        )
        result = cur.fetchone()
        assert result is not None        

        request = client.get('/3/1/drop_from_org')
        assert request.headers['location'] == 'http://localhost/1/org_page'

        # this member should be deleted from the roster
        cur.execute(
            '''
            SELECT * 
            FROM roster
            WHERE roster.org_id = 1
            AND roster.member_id = 3
            '''
        )
        result = cur.fetchone()
        assert result is None

        # other members in the org should not be deleted from roster
        cur.execute(
            '''
            SELECT * 
            FROM roster
            WHERE roster.org_id = 1
            AND roster.member_id = 2
            '''
        )
        result = cur.fetchone()
        assert result is not None

        # other members in the org should not be deleted from roster
        cur.execute(
            '''
            SELECT * 
            FROM roster
            WHERE roster.org_id = 1
            AND roster.member_id = 1
            '''
        )
        result = cur.fetchone 
        assert result is not None        

        # availability slot associated with organization should not be deleted
        cur.execute(
            '''
            SELECT * 
            FROM availability_slot
            WHERE availability_slot.avail_slot_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is not None

        # make sure member request associated with the member 
        # and the availability request has been deleted
        cur.execute(
            '''
            SELECT * 
            FROM member_request
            WHERE member_request.member_id = 3
            '''
        )
        result = cur.fetchone()
        assert result is None

        # this availability slot should not be deleted
        cur.execute(
            '''
            SELECT * 
            FROM availability_slot
            WHERE availability_slot.avail_slot_id = 2
            '''
        )
        result = cur.fetchone()
        assert result is not None

        # this member_request should not be deleted
        cur.execute(
            '''
            SELECT * 
            FROM member_request
            WHERE member_request.member_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is not None    
