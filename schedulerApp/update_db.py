from flask import session, Flask, redirect, flash, url_for
from datetime import datetime

from schedulerApp.db import get_db
from schedulerApp.util import return_datetime
from schedulerApp.query_db import(
    get_org_avail_requests, 
    get_avail_requests_data, 
    get_member_booked_dates, 
    get_org_booked_dates
) 
def insert_booked_date(avail_request_id, start_date, start_time, end_date, end_time, timezone):
    '''insert a booked_date into the database'''
    db = get_db()

    # get datetime objects for the start and end
    start_book = return_datetime(start_date, start_time, timezone)
    end_book = return_datetime(end_date, end_time, timezone)    

    # get timezone, org_id, and avail_request_name from avail_request
    # these fields are all carried over into the booked date
    avail_request_info = db.execute(
        '''
        SELECT 
        availability_request.timezone, 
        availability_request.org_id, 
        availability_request.avail_request_name
        FROM availability_request
        WHERE availability_request.avail_request_id = ?
        ''',
        (avail_request_id,)
    ).fetchone()

    tz = avail_request_info[0]
    org_id = avail_request_info[1]
    name = avail_request_info[2]

    # insert the booked date into the database
    db.execute(
        '''INSERT INTO booked_date(
            booked_date_name, start_time, end_time, timezone, org_id, avail_request_id
        ) VALUES (?,?,?,?,?,?)''',
        (name, start_book, end_book, tz, org_id, avail_request_id,)
    )
    db.commit()

    # update session data
    session['booked_dates'] = get_member_booked_dates(session['member_id'])
    session['org_booked_dates'] = get_org_booked_dates(session['active_org']['org_id'])
    session.modified = True

def insert_availability_slot(avail_request_id, start_date, start_time, end_date, end_time, timezone):
    '''insert an availability slot into the database'''
    db = get_db()
    # get datetime objects for start and end
    start_slot = return_datetime(start_date, start_time, timezone)
    end_slot = return_datetime(end_date, end_time, timezone)

    # insert new availability slot into the database
    db.execute(
        '''INSERT INTO availability_slot(
            start_slot, end_slot, avail_request_id, member_id
        ) VALUES (?,?,?,?)''',
        (start_slot, end_slot, avail_request_id, session['member_id'],)
    )

    # set the answered field in member_request to TRUE
    db.execute(
        ''' UPDATE member_request SET answered = TRUE WHERE member_id = ? AND avail_request_id = ? ''',
        (session['member_id'], avail_request_id,)
    )
    db.commit()

    # update session data 
    start_datetime = return_datetime(start_date, start_time).strftime("%-m/%-d/%Y %-I:%M%p")
    end_datetime = return_datetime(end_date, end_time).strftime("%-m/%-d/%Y %-I:%M%p")

    for response in session['member_responses']:
        if response['member_id'] == session['member_id']:
            response['answered'] = 1
            response['avail_slots'].append(
                {
                    'start_time': start_datetime,
                    'end_time': end_datetime
                }
            )
    session.modified = True    

def insert_availability_request(
            org_id,
            tz, 
            avail_request_name, 
            start_date, 
            start_time, 
            end_date, 
            end_time
        ):
    '''insert an availability request into the database'''
    db = get_db()
    # get datetime objects for start and end
    start_request = return_datetime(start_date, start_time, tz)
    end_request = return_datetime(end_date, end_time, tz)

    # insert new avaiability request into the database
    db.execute(
        ''' INSERT INTO availability_request 
        (avail_request_name, start_request, end_request, 
        timezone, org_id, completed) VALUES (?, ?, ?, ?, ?, ?)''',
        (avail_request_name, start_request, end_request, tz, org_id, False)
    )

    # in order to add to member_request we need to avail_request_id of the 
    # availability request we just created
    member_id = session.get('member_id')
    avail_request_id = db.execute(
        'SELECT last_insert_rowid()'
    ).fetchone()

    #insert everyone in the organization into member_request
    members_in_org = db.execute(
        'SELECT member_id FROM roster WHERE roster.org_id = ?',
        (org_id,)
    ).fetchall()

    for member in members_in_org:
        org_member_id = member[0] #member_id of a member in the org

        # insert this member and the avail_request id of the newly created 
        # availability request into member_id
        db.execute(
            '''
            INSERT INTO member_request (member_id, avail_request_id, answered) 
            VALUES (?,?,?)
            ''',
            (org_member_id, avail_request_id[0], False)
        )
    db.commit()

    #update session data
    session['avail_requests'] = get_avail_requests_data(session['member_id'])
    session['org_avail_requests'] = get_org_avail_requests(session['active_org']['org_id'])
    session.modified = True

def check_if_complete(avail_request_id):
    ''' check if an availability request has been answered by all
    members of its associated organization. '''
    db = get_db()
    answered_list = db.execute(
        '''
        SELECT answered FROM member_request WHERE member_request.avail_request_id = ?
        ''',
        (avail_request_id,)
    ).fetchall()

    for answer in answered_list:
        if answer[0] == 0:
            return False #there is at least one member who has not responded to the request

    #all members have answered so availability request is complete, update the database
    db.execute(
        '''
        UPDATE availability_request SET completed = TRUE 
        WHERE availability_request.avail_request_id = ?
        ''',
        (avail_request_id,)
    )
    db.commit()
    return True

def delete_availability_request(avail_request_id):
    '''delete an availability request from the database and update
    session'''
    db = get_db()
    db.execute(
        '''
        DELETE FROM availability_request
        WHERE availability_request.avail_request_id = ?
        ''',
        (avail_request_id,)
    )
    db.commit()

    # update session data
    session['avail_requests'] = get_avail_requests_data(session['member_id'])
    session['org_avail_requests'] = get_org_avail_requests(session['active_org']['org_id'])
    session.modified = True

def delete_booked_date(booked_date_id):
    '''delete a booked date from the database and update session'''
    db = get_db()
    db.execute(
        '''
        DELETE FROM booked_date
        WHERE booked_date.booked_date_id = ?
        ''',
        (booked_date_id,)
    )
    db.commit()

    # update session data
    session['booked_dates'] = get_member_booked_dates(session['member_id'])
    if session.get('active_org') is not None:
        session['org_booked_dates'] = get_org_booked_dates(session['active_org']['org_id'])
    session.modified = True

def update_availability_requests_by_member(member_id):
    '''delete all of the availability requests associated that are
    older than datetime.utcnow() and update the session data for all 
    availability requests associated with a member '''
    db = get_db()

    # delete old availability requests
    db.execute(
        '''
        DELETE FROM availability_request 
        WHERE availability_request.avail_request_id 
        IN (
            SELECT member_request.avail_request_id 
            FROM member_request
            WHERE member_request.member_id = ?
        )
        AND availability_request.end_request < ?
        ''',
        (member_id, datetime.utcnow())
    )

    db.commit()

    #update session data
    session['avail_requests'] = get_avail_requests_data(member_id)
    if session.get('active_org') is not None:
        session['org_avail_requests'] = get_org_avail_requests(session['active_org']['org_id'])
    session.modified = True

def update_availability_requests_by_org(org_id):
    '''delete all availability requests that are older than
    datetime.utcnow() and update availability request session data for 
    all availability requests associated with an organization'''
    db = get_db()

    # delete old availability requests
    db.execute(
        '''
        DELETE FROM availability_request 
        WHERE availability_request.avail_request_id 
        IN (
            SELECT availability_request.avail_request_id
            FROM availability_request
            WHERE availability_request.org_id = ?
        )
        AND availability_request.end_request < ?
        ''',
        (org_id, datetime.utcnow())
    )

    db.commit()

    #update session data
    session['avail_requests'] = get_avail_requests_data(session['member_id'])
    session['org_avail_requests'] = get_org_avail_requests(org_id)
    session.modified = True

def update_booked_dates_by_member(member_id):
    '''delete all booked dates that are older than 
    datetime.utcnow() and update the booked dates session data for 
    all booked dates associated with a member'''
    db = get_db()

    debug_data = db.execute(
        '''
        SELECT * 
        FROM booked_date
        WHERE booked_date.end_time < ?
        ''',
        (datetime.utcnow(),)
    ).fetchall()

    db.execute(
        '''
        DELETE FROM booked_date
        WHERE booked_date.org_id
        IN (
            SELECT roster.org_id 
            FROM roster
            WHERE roster.member_id = ? 
        )
        AND booked_date.end_time < ?
        ''',
        (member_id, datetime.utcnow())
    )

    db.commit()

    #update session data
    session['booked_dates'] = get_member_booked_dates(session['member_id'])
    if session.get('active_org') is not None:
        session['org_booked_dates'] = get_org_booked_dates(session['active_org']['org_id'])
    session.modified = True

def update_booked_dates_by_org(org_id):
    '''delete alll booked dates that are older than datetime.utcnow()
    and update booked date session data for all booked dates that are
    associated with an organization'''
    db = get_db()

    # delete old booked dates
    db.execute(
        '''
        DELETE FROM booked_date
        WHERE booked_date.org_id = ?
        AND booked_date.end_time < ?
        ''',
        (org_id, datetime.utcnow())
    )

    db.commit()

    #update session data
    session['booked_dates'] = get_member_booked_dates(session['member_id'])
    session['org_booked_dates'] = get_org_booked_dates(org_id)
    session.modified = True