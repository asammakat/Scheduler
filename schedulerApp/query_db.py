from flask import session

from schedulerApp.db import get_db
from schedulerApp.util import convert_datetime_to_user_tz


def get_member_booked_dates(member_id):
    '''create a list of dicts with information from all of the booked dates for a member
    to be displayed of the home page of that member. Each dict contains the keys
    'booked_date_name, 'start_time', 'end_time', and 'timezone'''
    db = get_db()

    member_booked_dates_from_db = db.execute(
        '''
        SELECT 
        booked_date.booked_date_name,
        booked_date.start_time,
        booked_date.end_time,
        booked_date.timezone
        FROM booked_date
        WHERE booked_date.org_id
        IN (
            SELECT roster.org_id
            FROM roster
            WHERE roster.member_id = ?
        )
        ''',
        (member_id,)
    ).fetchall()    

    member_booked_dates = []

    # create the dict objects for each booked date and append them to the list 
    # that will be returned
    for date in member_booked_dates_from_db:
        timezone = date[3]

        member_booked_date = {}
        member_booked_date['booked_date_name'] = date[0]
        member_booked_date['start_time'] = convert_datetime_to_user_tz(date[1], timezone)
        member_booked_date['end_time'] = convert_datetime_to_user_tz(date[2], timezone)
        member_booked_date['timezone'] = timezone

        member_booked_dates.append(member_booked_date)
    
    return member_booked_dates

def get_org_avail_requests(org_id):
    '''create a list of dicts containing information from all of the 
    availability requests assiciated with a particular organization to be displayed
    on the organization page. Each dict contains the keys 'avail_request_id',
    'avail_request_name', 'completed' and 'members_not_answered' '''
    db = get_db()

    # get the desired fields from all 
    # availability requests associated with an organization
    org_avail_requests_from_db = db.execute(
        '''
        SELECT 
        availability_request.avail_request_id,
        availability_request.avail_request_name,
        availability_request.completed
        FROM availability_request
        WHERE availability_request.org_id = ?
        ''',
        (org_id,)
    ).fetchall()

    org_avail_requests = []

    # create the dict object for each availability request and append them to the 
    # list that will be returned
    for org_avail_request in org_avail_requests_from_db:
        avail_request = {}
        avail_request['avail_request_id'] = org_avail_request[0]
        avail_request['avail_request_name'] = org_avail_request[1]
        avail_request['completed'] = org_avail_request[2]

        # get a list of all of the members who have not answered for the 
        members_not_answered_from_db = db.execute(
            '''
            SELECT member.username 
            FROM member 
            WHERE member.member_id 
            IN(
                SELECT member_request.member_id FROM  member_request 
                WHERE member_request.avail_request_id = ?
                AND member_request.answered = FALSE                
            )
            ''',
            (org_avail_request[0],) 
        ).fetchall()

        members_not_answered = []
        for member in members_not_answered_from_db:
            members_not_answered.append(member[0])
        
        avail_request['members_not_answered'] = members_not_answered
        org_avail_requests.append(avail_request)
    
    return org_avail_requests

def get_org_booked_dates(org_id):
    '''create a list of dicts containing information from all of the 
    booked_dates associated with an organization to be displayed on the 
    organization page. Each dict contains the keys 'booked_date_name',
    'booked_date_id', 'start_time', 'end_time' and 'timezone' '''
    db = get_db()

    # get the desired fields for all 
    # booked_dates associated with an organization
    org_booked_dates_from_db = db.execute(
        '''
        SELECT 
        booked_date.booked_date_name, 
        booked_date.booked_date_id,
        booked_date.start_time,
        booked_date.end_time,
        booked_date.timezone
        FROM booked_date
        WHERE booked_date.org_id = ?
        ''',
        (org_id,)
    ).fetchall()

    booked_dates = []

    # create a dict object for each booked date and append them 
    # to the list that will be returned
    for date in org_booked_dates_from_db:
        booked_date = {}        

        timezone = date[4]
        start_time = convert_datetime_to_user_tz(date[2], timezone)
        end_time = convert_datetime_to_user_tz(date[3], timezone)

        booked_date['booked_date_name'] = date[0]
        booked_date['booked_date_id'] = date[1]
        booked_date['start_time'] = start_time.strftime("%-m/%-d/%Y %-I:%M%p")
        booked_date['end_time'] = end_time.strftime("%-m/%-d/%Y %-I:%M%p")
        booked_date['timezone'] = timezone

        booked_dates.append(booked_date)

    return booked_dates

def get_avail_request(avail_request_id):
    '''get information for an availability request from the database 
    to display on the avail_request page'''
    db = get_db()

    # get desired fields for the availability request from the database
    avail_request_from_db = db.execute(
        '''SELECT 
           availability_request.avail_request_name, 
           availability_request.start_request,
           availability_request.end_request,
           availability_request.timezone,
           availability_request.org_id
           FROM availability_request
           WHERE avail_request_id = ?''',
           (avail_request_id,)
        ).fetchone()

    # create a dict to store availability request information
    avail_request = {}

    timezone = avail_request_from_db[3]
    start_time = convert_datetime_to_user_tz(avail_request_from_db[1], timezone)
    end_time = convert_datetime_to_user_tz(avail_request_from_db[2], timezone)

    avail_request['name'] = avail_request_from_db[0]
    avail_request['start'] = start_time.strftime("%-m/%-d/%Y %-I:%M%p")
    avail_request['end'] = end_time.strftime("%-m/%-d/%Y %-I:%M%p")
    avail_request['tz'] = timezone 
    avail_request['org_id'] = avail_request_from_db[4]

    return avail_request  

def get_avail_requests_data(member_id):
    '''Get a list of dicts containing data on all availability requests for a member 
    to be displayed on the home page for a member. Each dict contains the keys
    'avail_request_id', 'avail_request_name', 'org_name' and 'answered'.'''
    db = get_db()

    # get all of the availability request id's assiciated with a member
    avail_request_ids = db.execute(
        '''
        SELECT 
        availability_request.avail_request_id
        FROM availability_request 
        WHERE availability_request.avail_request_id 
        IN(
            SELECT avail_request_id FROM member_request WHERE member_request.member_id = ?
        )
        ''',
        (member_id, )
    ).fetchall()

    avail_requests = []

    # create a dict object for each availability request and append them 
    # to the list that will be returned
    for elem in avail_request_ids:
        avail_request_id = elem[0] #elem is a tuple

        avail_request_name = db.execute(
            '''
            SELECT availability_request.avail_request_name
            FROM availability_request
            WHERE availability_request.avail_request_id = ?
            ''',
            (avail_request_id,)
        ).fetchone()[0]

        org_name = db.execute(
            '''
            SELECT organization.org_name 
            FROM organization 
            WHERE organization.org_id
            IN(
                SELECT organization.org_id FROM availability_request WHERE availability_request.avail_request_id = ?
            )
            ''',
            (avail_request_id,)
        ).fetchone()[0]

        answered = db.execute(
            '''
            SELECT member_request.answered 
            FROM member_request 
            WHERE member_request.avail_request_id = ?
            AND member_request.member_id = ?
            ''',
            (avail_request_id, session['member_id'])
        ).fetchone()[0]

        # build the dict with relavant information for the avail request
        request_data = {}
        request_data['avail_request_id'] = avail_request_id
        request_data['avail_request_name'] = avail_request_name
        request_data['org_name'] = org_name
        request_data['answered'] = answered
        
        avail_requests.append(request_data)
    return avail_requests

def get_member_info(avail_request_id):
    '''Build a list of dicts of all of the usernames, their answered status, 
    and the start and end times of any availability slots they have created 
    in association with a particular availability request to be displayed on 
    the availability request page and the book page.'''
    db = get_db()
    members = []

    # get timzone of the avail request to convert avail_slot times from UTC
    timezone = db.execute(
        '''
        SELECT availability_request.timezone
        FROM availability_request
        WHERE avail_request_id = ?
        ''',
        (avail_request_id,)
    ).fetchone()[0]

    # get each member and their answered status associated with the availability request
    roster = db.execute(
        '''
        SELECT member_request.member_id, member_request.answered
        FROM member_request 
        WHERE member_request.avail_request_id = ?
        ''',
        (avail_request_id, )
    ).fetchall()

    for r in roster:
        member = {}
        #get the member's username
        username = db.execute(
            '''
            SELECT member.username 
            FROM member
            WHERE member_id = ?
            ''',
            [r[0]] #member_id of user
        ).fetchone()
        member['username'] = username[0]

        # get any availability slots the member has created 
        # in assiciation with the availability_request
        slots_from_db = db.execute(
            '''
            SELECT availability_slot.start_slot, availability_slot.end_slot 
            FROM   availability_slot
            WHERE  availability_slot.avail_request_id = ? AND availability_slot.member_id = ?
            ''',
            (avail_request_id, r[0],)
        ).fetchall()

        member['answered'] = r[1] # answered status associated with member_id 

        slots = []
        
        #grab the start and end times for each availability_slot the member has created
        for s in slots_from_db:
            slot = {}

            start_time = convert_datetime_to_user_tz(s[0], timezone)
            end_time = convert_datetime_to_user_tz(s[1], timezone)

            slot['start_time'] = start_time.strftime("%-m/%-d/%Y %-I:%M%p")
            slot['end_time'] = end_time.strftime("%-m/%-d/%Y %-I:%M%p")
            slots.append(slot)
        
        member['avail_slots'] = slots

        members.append(member)
    return members