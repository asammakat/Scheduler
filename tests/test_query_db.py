import pytest
import flask
from flask import session

from schedulerApp.db import get_db

def test_find_dates_in_common(client, auth, app):
    # make sure that first availability slot was added
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        with client:
            # login member 1 and make an avail slot
            auth.login() 
            assert session['member_id'] == 1
            auth.make_avail_request()

            # no dates have been added so dates in common should be an empty dict
            client.get('/1/avail_request')
            assert session['dates_in_common'] == []
            
            auth.add_avail_slot()

            # test that slot was successfully added
            cur.execute(
                "SELECT * FROM availability_slot where member_id = 1", 
            )
            result = cur.fetchone()
            assert result is not None

            # only one member has responded so dates in common should be an empty dict
            client.get('/1/avail_request')
            assert session['dates_in_common'] == []

            client.get('/logout') 

            # login member 2 and make an avail slot
            auth.login('other', 'test')
            assert session['member_id'] == 2
            auth.add_avail_slot(start_time='11:00a', end_time='12:00p')

            # test that slot was successfully added
            cur.execute(
                "SELECT * FROM availability_slot WHERE member_id = 2", 
            )
            result = cur.fetchone()
            assert result is not None

            # two members have answered so common time should appear
            client.get('/1/avail_request')
            assert session['dates_in_common'] == [
                {
                    'start_time': '1/1/2030 11:00AM', 
                    'end_time': '1/1/2030 12:00PM'
                }
            ]

            # test that multiple slots can be added
            auth.add_avail_slot(start_time='12:01p', end_time='12:30p')

            # test that slot was successfully added
            cur.execute(
                "SELECT * FROM availability_slot WHERE avail_slot_id = 3", 
            )
            result = cur.fetchone()
            assert result is not None

            client.get('/1/avail_request')
            assert session['dates_in_common'] == [
                {
                    'start_time': '1/1/2030 11:00AM', 
                    'end_time': '1/1/2030 12:00PM'
                },
                {
                    'start_time': '1/1/2030 12:01PM',
                    'end_time': '1/1/2030 12:30PM'
                }
            ]

            # test that more than two members can answer
            # login member 3 and add avail slot
            client.get('/logout')

            auth.login('Tim', 'test')
            assert session['member_id'] == 3

            auth.add_avail_slot(start_time='11:15a', end_time='11:45a')

            # test that slot was successfully added
            cur.execute(
                "SELECT * FROM availability_slot WHERE member_id = 3", 
            )
            result = cur.fetchone()
            assert result is not None            

            # new avail slot should affect date_in_common
            client.get('/1/avail_request')
            assert session['dates_in_common'] == [
                {
                    'start_time': '1/1/2030 11:15AM', 
                    'end_time': '1/1/2030 11:45AM'
                }
            ]

            #test that more than two members can result in more than one date in common 
            auth.add_avail_slot(start_time='12:15p', end_time='12:20p')

            # test that slot was successfully added
            cur.execute(
                "SELECT * FROM availability_slot WHERE avail_slot_id = 5", 
            )
            result = cur.fetchone()
            assert result is not None    

            # new avail slot should affect date_in_common
            client.get('/1/avail_request')
            assert session['dates_in_common'] == [
                {
                    'start_time': '1/1/2030 11:15AM', 
                    'end_time': '1/1/2030 11:45AM'
                },
                {
                    'start_time': '1/1/2030 12:15PM',
                    'end_time': '1/1/2030 12:20PM'
                }
            ]            

def test_find_dates_in_common_bracked_results(client, auth, app):
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        with client:
            # login member 1 and make an avail slot
            auth.login() 
            assert session['member_id'] == 1
            auth.make_avail_request()

            # no dates have been added so dates in common should be an empty dict
            client.get('/1/avail_request')
            assert session['dates_in_common'] == []
            
            auth.add_avail_slot()

            # test that slot was successfully added
            cur.execute(
                "SELECT * FROM availability_slot where member_id = 1", 
            )
            result = cur.fetchone()
            assert result is not None

            # only one member has responded so dates in common should be an empty dict
            client.get('/1/avail_request')
            assert session['dates_in_common'] == []   

            client.get('/logout') 

            # login member 2 and make an avail slot
            auth.login('other', 'test')
            assert session['member_id'] == 2
            auth.add_avail_slot(start_time='9:00a', end_time='1:30p')

            # test that slot was successfully added
            cur.execute(
                "SELECT * FROM availability_slot WHERE member_id = 2", 
            )
            result = cur.fetchone()
            assert result is not None

            # second avail slot bracketed the first so result should remain unchanged
            client.get('/1/avail_request')
            assert session['dates_in_common'] == [
                {
                    'start_time': '1/1/2030 10:00AM', 
                    'end_time': '1/1/2030 1:00PM'
                }
            ]    

def test_find_dates_in_common_all_dates_before(client, auth, app):
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        with client:
            # login member 1 and make an avail slot
            auth.login() 
            assert session['member_id'] == 1
            auth.make_avail_request()

            # no dates have been added so dates in common should be an empty dict
            client.get('/1/avail_request')
            assert session['dates_in_common'] == []
            
            auth.add_avail_slot()

            # test that slot was successfully added
            cur.execute(
                "SELECT * FROM availability_slot where member_id = 1", 
            )
            result = cur.fetchone()
            assert result is not None

            # only one member has responded so dates in common should be an empty dict
            client.get('/1/avail_request')
            assert session['dates_in_common'] == []    

            client.get('/logout') 

            # login member 2 and make an avail slot
            auth.login('other', 'test')
            assert session['member_id'] == 2
            auth.add_avail_slot(start_time='9:00a', end_time='9:30a')

            # test that slot was successfully added
            cur.execute(
                "SELECT * FROM availability_slot WHERE member_id = 2", 
            )
            result = cur.fetchone()
            assert result is not None

            # second avail slot does not cross first so no avail slots should be added
            client.get('/1/avail_request')
            assert session['dates_in_common'] == []
        
def test_find_dates_in_common_all_dates_after(client, auth, app):
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        with client:
            # login member 1 and make an avail slot
            auth.login() 
            assert session['member_id'] == 1
            auth.make_avail_request()

            # no dates have been added so dates in common should be an empty dict
            client.get('/1/avail_request')
            assert session['dates_in_common'] == []
            
            auth.add_avail_slot()

            # test that slot was successfully added
            cur.execute(
                "SELECT * FROM availability_slot where member_id = 1", 
            )
            result = cur.fetchone()
            assert result is not None

            # only one member has responded so dates in common should be an empty dict
            client.get('/1/avail_request')
            assert session['dates_in_common'] == []    

            client.get('/logout') 

            # login member 2 and make an avail slot
            auth.login('other', 'test')
            assert session['member_id'] == 2
            auth.add_avail_slot(start_time='1:01p', end_time='1:59p')

            # test that slot was successfully added
            cur.execute(
                "SELECT * FROM availability_slot WHERE member_id = 2", 
            )
            result = cur.fetchone()
            assert cur is not None

            # second avail slot does not cross first so no avail slots should be added
            client.get('/1/avail_request')
            assert session['dates_in_common'] == []
        
def test_find_dates_in_common_two_good_dates_last_bad(client, auth, app):
    with app.app_context():
            db = get_db()
            cur = db.cursor()
            with client:
                # login member 1 and make an avail slot
                auth.login() 
                assert session['member_id'] == 1
                auth.make_avail_request()

                # no dates have been added so dates in common should be an empty dict
                client.get('/1/avail_request')
                assert session['dates_in_common'] == []
                
                auth.add_avail_slot()

                # test that slot was successfully added
                cur.execute(
                    "SELECT * FROM availability_slot where member_id = 1", 
                )
                result = cur.fetchone()
                assert result is not None

                # only one member has responded so dates in common should be an empty dict
                client.get('/1/avail_request')
                assert session['dates_in_common'] == []

                client.get('/logout') 

                # login member 2 and make an avail slot
                auth.login('other', 'test')
                assert session['member_id'] == 2
                auth.add_avail_slot(start_time='11:00a', end_time='12:00p')

                # test that slot was successfully added
                cur.execute(
                    "SELECT * FROM availability_slot WHERE member_id = 2", 
                )
                result = cur.fetchone()
                assert result is not None

                # two members have answered so common time should appear
                client.get('/1/avail_request')
                assert session['dates_in_common'] == [
                    {
                        'start_time': '1/1/2030 11:00AM', 
                        'end_time': '1/1/2030 12:00PM'
                    }
                ]

                # test that more than two members can answer
                # login member 3 and add avail slot
                client.get('/logout')

                auth.login('Tim', 'test')
                assert session['member_id'] == 3

                auth.add_avail_slot(start_time='2:00a', end_time='2:30a')

                # test that slot was successfully added
                cur.execute(
                    "SELECT * FROM availability_slot WHERE member_id = 3", 
                )
                result = cur.fetchone()
                assert result is not None            

                # new avail slot should affect date_in_common
                client.get('/1/avail_request')
                assert session['dates_in_common'] == []


def test_find_dates_in_common_two_good_dates_second_bad(client, auth, app):
    with app.app_context():
            db = get_db()
            cur = db.cursor()
            with client:
                # login member 1 and make an avail slot
                auth.login() 
                assert session['member_id'] == 1
                auth.make_avail_request()

                # no dates have been added so dates in common should be an empty dict
                client.get('/1/avail_request')
                assert session['dates_in_common'] == []
                
                auth.add_avail_slot()

                # test that slot was successfully added
                cur.execute(
                    "SELECT * FROM availability_slot where member_id = 1", 
                )
                result = cur.fetchone()
                assert result is not None

                # only one member has responded so dates in common should be an empty dict
                client.get('/1/avail_request')
                assert session['dates_in_common'] == []

                client.get('/logout') 

                # login member 2 and make an avail slot
                auth.login('other', 'test')
                assert session['member_id'] == 2
                auth.add_avail_slot(start_time='2:00a', end_time='2:30a')

                # test that slot was successfully added
                cur.execute(
                    "SELECT * FROM availability_slot WHERE member_id = 2", 
                )
                result = cur.fetchone()
                assert result is not None

                # two members have answered so common time should appear
                client.get('/1/avail_request')
                assert session['dates_in_common'] == []

                # test that more than two members can answer
                # login member 3 and add avail slot
                client.get('/logout')

                auth.login('Tim', 'test')
                assert session['member_id'] == 3

                auth.add_avail_slot(start_time='11:00a', end_time='12:00p')

                # test that slot was successfully added
                cur.execute(
                    "SELECT * FROM availability_slot WHERE member_id = 3", 
                )
                result = cur.fetchone()
                assert result is not None            

                # new avail slot should affect date_in_common
                client.get('/1/avail_request')
                assert session['dates_in_common'] == []

def test_find_dates_in_common_two_good_dates_first_bad(client, auth, app):
    with app.app_context():
            db = get_db()
            cur = db.cursor()
            with client:
                # login member 1 and make an avail slot
                auth.login() 
                assert session['member_id'] == 1
                auth.make_avail_request()

                # no dates have been added so dates in common should be an empty dict
                client.get('/1/avail_request')
                assert session['dates_in_common'] == []
                
                auth.add_avail_slot(start_time='2:00a', end_time='2:30a')

                # test that slot was successfully added
                cur.execute(
                    "SELECT * FROM availability_slot where member_id = 1", 
                )
                result = cur.fetchone()
                assert result is not None

                # only one member has responded so dates in common should be an empty dict
                client.get('/1/avail_request')
                assert session['dates_in_common'] == []

                client.get('/logout') 

                # login member 2 and make an avail slot
                auth.login('other', 'test')
                assert session['member_id'] == 2
                auth.add_avail_slot()

                # test that slot was successfully added
                cur.execute(
                    "SELECT * FROM availability_slot WHERE member_id = 2", 
                )
                result = cur.fetchone()
                assert result is not None

                # two members have answered so common time should appear
                client.get('/1/avail_request')
                assert session['dates_in_common'] == []

                # test that more than two members can answer
                # login member 3 and add avail slot
                client.get('/logout')

                auth.login('Tim', 'test')
                assert session['member_id'] == 3

                auth.add_avail_slot(start_time='11:00a', end_time='12:00p')

                # test that slot was successfully added
                cur.execute(
                    "SELECT * FROM availability_slot WHERE member_id = 3", 
                )
                result = cur.fetchone()
                assert result is not None            

                # new avail slot should affect date_in_common
                client.get('/1/avail_request')
                assert session['dates_in_common'] == []