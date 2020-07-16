import pytest
import datetime

from schedulerApp.update_db import *
from schedulerApp.db import get_db

def test_update_availability_requests_by_member(app, auth, client):

    timezone = "America/Los_Angeles"
    org_id = 1    

    with app.app_context():
        db = get_db()
        cur = db.cursor()
        auth.login()
        assert client.get('/').status_code == 200        
        auth.make_avail_request(
            org_id=org_id,
            avail_request_name="TestAR",
            start_date='1/1/2030',
            start_time='6:00a',
            end_date='1/1/2030',
            end_time='7:00a',
            tz=timezone
        )

        # double check that insert was successful
        cur.execute(
            '''
            SELECT * FROM availability_request 
            WHERE avail_request_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is not None     

        client.get('/')  

        # date was not old so should not be deleted
        cur.execute(
            '''
            SELECT * FROM availability_request 
            WHERE avail_request_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is not None     

        #make an old avail request
        auth.make_avail_request(
            org_id=org_id,
            avail_request_name="TestAROld1",
            start_date='1/1/2019',
            start_time='6:00a',
            end_date='1/1/2019',
            end_time='7:00a',
            tz=timezone
        )     
             
        # double check that inserts were successful
        # avail_request_id is 2 
        cur.execute(
            '''
            SELECT * FROM availability_request 
            WHERE avail_request_id = 2
            '''
        )
        result = cur.fetchone()
        assert result is not None   

        cur.execute(
            '''
            SELECT * FROM member_request
            WHERE member_request.avail_request_id = 2
            '''
        )
        result = cur.fetchone()
        assert result is not None 

        client.get('/')

        #Availability requests were old so these shold now be deleted
        cur.execute(
            '''
            SELECT * FROM availability_request 
            WHERE avail_request_id = 2
            '''
        )
        result = cur.fetchone()
        assert result is None   

        cur.execute(
            '''
            SELECT * FROM member_request
            WHERE member_request.avail_request_id = 2
            '''
        )
        result = cur.fetchone()
        assert result is None       

        #TODO: test that old avail request made by other user is not deleted
                  
def test_update_booked_dates_by_member(app, auth, client):
    org_id = 1
    timezone = "America/Los_Angeles"

    with app.app_context():
        db = get_db()
        cur = db.cursor()
        auth.login()
        auth.make_avail_request()

        # book a date that is not old
        auth.book(
            start_date='1/1/2030',
            start_time='6:00a',
            end_date='1/1/2030',
            end_time='7:00a'
        )

        # check that booked date was added
        cur.execute(
            '''
            SELECT * FROM booked_date
            WHERE booked_date_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is not None

        client.get('/')

        # booked date was not old so should not be deleted
        cur.execute(
            '''
            SELECT * FROM booked_date
            WHERE booked_date_id = 1
            '''
        )
        result = cur.fetchone()
        assert result is not None        

        # book an old date
        auth.book(
            start_date='1/1/2019',
            start_time='6:00a',
            end_date='1/1/2019',
            end_time='7:00a'
        )

        # home page has not been visited so this should not be deleted
        cur.execute(
            '''
            SELECT * FROM booked_date
            WHERE booked_date_id = 2
            '''
        )
        result = cur.fetchone()
        assert result is not None       

        client.get('/')

        # booked date was old so it should be deleted
        cur.execute(
            '''
            SELECT * FROM booked_date
            WHERE booked_date_id = 2
            '''
        )
        result = cur.fetchone()
        assert result is None    

        #TODO: test that old booked date made by other user is not deleted           

def test_update_availability_requests_by_org(app, auth, client):

    org_id = 1
    timezone = "America/Los_Angeles"

    with app.app_context():
        db = get_db()
        cur = db.cursor()
        auth.login()
        assert client.get('/1/org_page').status_code == 200        
        auth.make_avail_request(
            org_id=org_id,
            avail_request_name="TestAR",
            start_date='1/1/2030',
            start_time='6:00a',
            end_date='1/1/2030',
            end_time='7:00a',
            tz=timezone
        )

        client.get('/1/org_page')

        # date was not old so should not be deleted
        cur.execute(
            '''
            SELECT * FROM availability_request 
            WHERE avail_request_id = 1
            '''
        )
        result = cur.fetchone() 
        assert result is not None   

        cur.execute(
            '''
            SELECT * FROM member_request
            WHERE member_request.avail_request_id = 1
            '''
        )
        result = cur.fetchone() 
        assert result is not None
    
        #make an old avail request
        auth.make_avail_request(
            org_id=org_id,
            avail_request_name="TestAROld1",
            start_date='1/1/2019',
            start_time='6:00a',
            end_date='1/1/2019',
            end_time='7:00a',
            tz=timezone
        )

        #Org page has not been visited so these should not be deleted yet
        cur.execute(
            '''
            SELECT * FROM availability_request 
            WHERE avail_request_id = 2
            '''
        )
        result = cur.fetchone() 
        assert result is not None   

        cur.execute(
            '''
            SELECT * FROM member_request
            WHERE member_request.avail_request_id = 2
            '''
        )
        result = cur.fetchone() 
        assert result is not None        

        client.get('/1/org_page')
    
        #Availability requests were old so these shold now be deleted
        cur.execute(
            '''
            SELECT * FROM availability_request 
            WHERE avail_request_id = 2
            '''
        )
        result = cur.fetchone()
        assert result is None   


        cur.execute(
            '''
            SELECT * FROM member_request
            WHERE member_request.avail_request_id = 2
            '''
        )
        result = cur.fetchone()
        assert result is None  

    #TODO:  Test that old avail request from other org is not deleted    

def test_update_booked_dates_by_org(app, auth, client):

    org_id = 1
    timezone = "America/Los_Angeles"

    with app.app_context():
        db = get_db()
        cur = db.cursor()
        auth.login()
        auth.make_avail_request()

        # book a date that is not old
        auth.book(
            start_date='1/1/2030',
            start_time='6:00a',
            end_date='1/1/2030',
            end_time='7:00a'
        )

        # check that booked date was added
        cur.execute(
            '''
            SELECT * FROM booked_date
            WHERE booked_date_id = 1
            '''
        )
        
        result = cur.fetchone() 
        assert result is not None

        client.get('/1/org_page')

        # booked date was not old so should not be deleted
        cur.execute(
            '''
            SELECT * FROM booked_date
            WHERE booked_date_id = 1
            '''
        )
        
        result = cur.fetchone() 
        
        assert result is not None        

        # book an old date
        auth.book(
            start_date='1/1/2019',
            start_time='6:00a',
            end_date='1/1/2019',
            end_time='7:00a'
        )

        # home page has not been visited so this should not be deleted
        cur.execute(
            '''
            SELECT * FROM booked_date
            WHERE booked_date_id = 2
            '''
        )
        result = cur.fetchone() 
        assert result is not None       

        client.get('/1/org_page')

        # booked date was old so it should be deleted
        cur.execute(
            '''
            SELECT * FROM booked_date
            WHERE booked_date_id = 2
            '''
        )
        result = cur.fetchone() 
        assert result is None    

        #TODO: test that old booked date made by other user is not deleted