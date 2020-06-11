import pytest
import datetime

from schedulerApp.update_db import *
from schedulerApp.db import get_db

def test_delete_old_availability_requests_by_member(app):

    avail_request_name = "TestAR"
    start_request = datetime(2030, 1, 1, 6, 0)
    end_request = datetime(2030, 1, 1, 7, 0)
    timezone = "America/Los_Angeles"
    org_id = 1

    with app.app_context():
        db = get_db()
        delete_old_availability_requests_by_member(1)

        #avail_request_id is 1
        db.execute(
            '''
            INSERT INTO availability_request (
                avail_request_name,
                start_request,
                end_request,
                timezone,
                org_id
            )
            VALUES (?,?,?,?,?)
            ''',
            (avail_request_name, start_request, end_request, timezone, org_id)
        )

        db.execute(
            '''
            INSERT INTO member_request(
                member_id,
                avail_request_id, 
                answered
            )
            VALUES (?,?,?)
            ''',
            (1,1,0)

        )
        
        db.commit()

        # double check that insert was successful
        assert db.execute(
            '''
            SELECT * FROM availability_request 
            WHERE avail_request_id = 1
            '''
        ).fetchone() is not None    

        delete_old_booked_dates_by_member(1)

        # deleting booked dates should not effect avail_requests
        assert db.execute(
            '''
            SELECT * FROM availability_request 
            WHERE avail_request_id = 1
            '''
        ).fetchone() is not None            

        delete_old_availability_requests_by_member(1) 

        #availability request is not old so it should not be deleted
        assert db.execute(
            '''
            SELECT * FROM availability_request 
            WHERE avail_request_id = 1
            '''
        ).fetchone() is not None

        avail_request_name = 'testAR1'
        start_request = datetime(2019, 1, 1, 6, 0)
        end_request = datetime(2019, 1, 1, 7, 0)  

        # avail_request_id is 2
        db.execute(
            '''
            INSERT INTO availability_request (
                avail_request_name,
                start_request,
                end_request,
                timezone,
                org_id
            )
            VALUES (?,?,?,?,?)
            ''',
            (avail_request_name, start_request, end_request, timezone, org_id)
        )

        db.execute(
            '''
            INSERT INTO member_request (
                member_id,
                avail_request_id, 
                answered
            )
            VALUES (?,?,?)
            ''',
            (1,2,0)
        )

        avail_request_name = 'testAR2'

        # avail_request_id is 3
        db.execute(
            '''
            INSERT INTO availability_request (
                avail_request_name,
                start_request,
                end_request,
                timezone,
                org_id
            )
            VALUES (?,?,?,?,?)
            ''',
            (avail_request_name, start_request, end_request, timezone, org_id)
        )

        db.execute(
            '''
            INSERT INTO member_request (
                member_id,
                avail_request_id, 
                answered
            )
            VALUES (?,?,?)
            ''',
            (2,3,0)
        )        
        
        db.commit()        

        # double check that inserts were successful
        assert db.execute(
            '''
            SELECT * FROM availability_request 
            WHERE availability_request.avail_request_id = 2
            '''
        ).fetchone() is not None      

        assert db.execute(
            '''
            SELECT * FROM member_request
            WHERE member_request.avail_request_id = 2
            '''
        ).fetchone() is not None 

        assert db.execute(
            '''
            SELECT * FROM availability_request 
            WHERE availability_request.avail_request_id = 3
            '''
        ).fetchone() is not None         

        delete_old_availability_requests_by_member(1)

        # delete function above should delete this avail request
        assert db.execute(
            '''
            SELECT * FROM availability_request 
            WHERE avail_request_id = 2
            '''
        ).fetchone() is None       

        assert db.execute(
            '''
            SELECT * FROM member_request
            WHERE member_request.avail_request_id = 2
            '''
        ).fetchone() is None         

        # member_id is not associated with this avail request so it should not be deleted
        assert db.execute(
            '''
            SELECT * FROM availability_request 
            WHERE availability_request.avail_request_id = 3
            '''
        ).fetchone() is not None   

        assert db.execute(
            '''
            SELECT * FROM member_request
            WHERE member_request.avail_request_id = 3
            '''
        ).fetchone() is not None     
              
        
                  
def test_delete_old_booked_dates_by_member(app):

    avail_request_name = "TestAR" 
    booked_date_name = "TestBD"
    start_time = datetime(2030, 1, 1, 6, 0)
    end_time = datetime(2030, 1, 1, 7, 0)
    timezone = "America/Los_Angeles"
    org_id = 1

    with app.app_context():
        db = get_db()
        delete_old_booked_dates_by_member(1)

        avail_request_id = 1
        db.execute(
            '''
            INSERT INTO availability_request (
                avail_request_name,
                start_request,
                end_request,
                timezone,
                org_id
            )
            VALUES (?,?,?,?,?)
            ''',
            (avail_request_name, start_time, end_time, timezone, org_id)
        )        

        db.execute(
            '''
            INSERT INTO booked_date (
                booked_date_name,
                start_time,
                end_time,
                timezone,
                org_id,
                avail_request_id
            )
            VALUES (?,?,?,?,?,?)
            ''',
            (booked_date_name, start_time, end_time, timezone, org_id, avail_request_id)
        )
        
        db.commit()

        delete_old_availability_requests_by_member(1)

        # booked date should not be deleted when delete_old_availability_requests is called
        assert db.execute(
            '''
            SELECT * FROM booked_date
            WHERE booked_date_id = 1
            '''
        ).fetchone() is not None

        booked_date_name = 'testBD1'
        start_time = datetime(2019, 1, 1, 6, 0)
        end_time = datetime(2019, 1, 1, 7, 0)

        delete_old_booked_dates_by_member(1)

        # booked date is not old so should not be deleted
        assert db.execute(
            '''
            SELECT * FROM booked_date
            WHERE booked_date_id = 1
            '''
        ).fetchone() is not None        

        avail_request_id = 2
        db.execute(
            '''
            INSERT INTO availability_request (
                avail_request_name,
                start_request,
                end_request,
                timezone,
                org_id
            )
            VALUES (?,?,?,?,?)
            ''',
            (avail_request_name, start_time, end_time, timezone, org_id)
        )

        db.execute( #BUG having this member_request stops the delete from happening
            '''
            INSERT INTO member_request (
                member_id,
                avail_request_id,
                answered
            )
            VALUES (?,?,?)
            ''',
            (1,2,0)
        )

        db.execute(
            '''
            INSERT INTO booked_date (
                booked_date_name,
                start_time,
                end_time,
                timezone,
                org_id,
                avail_request_id
            )
            VALUES (?,?,?,?,?,?)
            ''',
            (avail_request_name, start_time, end_time, timezone, org_id, avail_request_id)
        )    

        db.execute(
            '''
            INSERT INTO booked_date (
                booked_date_name,
                start_time,
                end_time,
                timezone,
                org_id,
                avail_request_id
            )
            VALUES (?,?,?,?,?,?)
            ''',
            (booked_date_name, start_time, end_time, timezone, org_id, avail_request_id)
        )

        db.commit()

        # double check that above inserts were successful
        assert db.execute(
            '''
            SELECT * FROM availability_request 
            WHERE availability_request.avail_request_id = 2
            '''
        ).fetchone() is not None      

        assert db.execute(
            '''
            SELECT * FROM booked_date 
            WHERE booked_date.avail_request_id = 2
            '''
        ).fetchone() is not None      


        delete_old_availability_requests_by_member(1) #BUG this stops the dete from booked_date

        # deleting the availability_requests should not delete the booked date
        assert db.execute(
            '''
            SELECT * FROM booked_date 
            WHERE booked_date.booked_date_name = 'testBD1'
            '''
        ).fetchone() is not None    

        delete_old_booked_dates_by_member(1)       

        # booked_date should now be deleted
        assert db.execute(
            '''
            SELECT * FROM booked_date 
            WHERE booked_date.avail_request_id = 'testBD1'
            '''
        ).fetchone() is None    

def test_delete_old_availability_requests_by_org(app):
    avail_request_name = "TestAR"
    start_request = datetime(2030, 1, 1, 6, 0)
    end_request = datetime(2030, 1, 1, 7, 0)
    timezone = "America/Los_Angeles"
    org_id = 1

    with app.app_context():
        db = get_db()
        delete_old_availability_requests_by_org(1)

        #avail_request_id is 1
        db.execute(
            '''
            INSERT INTO availability_request (
                avail_request_name,
                start_request,
                end_request,
                timezone,
                org_id
            )
            VALUES (?,?,?,?,?)
            ''',
            (avail_request_name, start_request, end_request, timezone, org_id)
        )
        
        db.commit()

        # check that insert was successful
        assert db.execute(
            '''
            SELECT * FROM availability_request
            WHERE availability_request.avail_request_id = 1
            '''
        ).fetchone() is not None

        delete_old_availability_requests_by_org(1)

        #dates are not old so should have no effect
        assert db.execute(
            '''
            SELECT * FROM availability_request
            WHERE availability_request.avail_request_id = 1
            '''
        ).fetchone() is not None

        avail_request_name = "TestAR2"
        start_request = datetime(2019, 1, 1, 6, 0)
        end_request = datetime(2019, 1, 1, 7, 0)     
        
        #avail_request_id is 2
        db.execute(
            '''
            INSERT INTO availability_request (
                avail_request_name,
                start_request,
                end_request,
                timezone,
                org_id
            )
            VALUES (?,?,?,?,?)
            ''',
            (avail_request_name, start_request, end_request, timezone, org_id)
        )
        
        db.commit()

        # check that insert was successful
        assert db.execute(
            '''
            SELECT * FROM availability_request
            WHERE availability_request.avail_request_id = 2
            '''
        ).fetchone() is not None        

        delete_old_availability_requests_by_org(2)

        # The org for avail_request is 1 so this should have no effect        
        assert db.execute(
            '''
            SELECT * FROM availability_request
            WHERE availability_request.avail_request_id = 2
            '''
        ).fetchone() is not None             

        delete_old_availability_requests_by_org(1)

        #the avail request sholud not be deleted
        assert db.execute(
            '''
            SELECT * FROM availability_request
            WHERE availability_request.avail_request_id = 2
            '''
        ).fetchone() is None

def test_delete_old_booked_dates_by_org(app):

    avail_request_name = "TestAR" 
    booked_date_name = "TestBD"
    start_time = datetime(2030, 1, 1, 6, 0)
    end_time = datetime(2030, 1, 1, 7, 0)
    timezone = "America/Los_Angeles"
    org_id = 1

    with app.app_context():
        db = get_db()
        delete_old_booked_dates_by_member(1)

        avail_request_id = 1
        db.execute(
            '''
            INSERT INTO availability_request (
                avail_request_name,
                start_request,
                end_request,
                timezone,
                org_id
            )
            VALUES (?,?,?,?,?)
            ''',
            (avail_request_name, start_time, end_time, timezone, org_id)
        )    

        db.execute(
            '''
            INSERT INTO booked_date (
                booked_date_name,
                start_time,
                end_time,
                timezone,
                org_id,
                avail_request_id
            )
            VALUES (?,?,?,?,?,?)
            ''',
            (booked_date_name, start_time, end_time, timezone, org_id, avail_request_id)
        )

        db.commit()        

        delete_old_availability_requests_by_org(1)

        # booked date should not be deleted when delete_old_availability_requests is called
        assert db.execute(
            '''
            SELECT * FROM booked_date
            WHERE booked_date_id = 1
            '''
        ).fetchone() is not None

        delete_old_booked_dates_by_org(1)

        #not old dates so nothing should be deleted
        assert db.execute(
            '''
            SELECT * FROM booked_date
            WHERE booked_date_id = 1
            '''
        ).fetchone() is not None        

        avail_request_name = "TestAR1" 
        booked_date_name = "TestBD1"
        start_time = datetime(2019, 1, 1, 6, 0)
        end_time = datetime(2019, 1, 1, 7, 0)

        avail_request_id = 2
        db.execute(
            '''
            INSERT INTO availability_request (
                avail_request_name,
                start_request,
                end_request,
                timezone,
                org_id
            )
            VALUES (?,?,?,?,?)
            ''',
            (avail_request_name, start_time, end_time, timezone, org_id)
        )    

        db.execute(
            '''
            INSERT INTO booked_date (
                booked_date_name,
                start_time,
                end_time,
                timezone,
                org_id,
                avail_request_id
            )
            VALUES (?,?,?,?,?,?)
            ''',
            (booked_date_name, start_time, end_time, timezone, org_id, avail_request_id)
        )
        db.commit()        

        delete_old_availability_requests_by_org(1)

        # booked date should not be deleted when delete_old_availability_requests is called
        assert db.execute(
            '''
            SELECT * FROM booked_date
            WHERE booked_date_id = 2
            '''
        ).fetchone() is not None

        delete_old_booked_dates_by_org(1)

        #booked date is old so it should be deleted
        assert db.execute(
            '''
            SELECT * FROM booked_date
            WHERE booked_date_id = 2
            '''
        ).fetchone() is None        