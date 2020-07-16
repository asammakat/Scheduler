from flask import session
from datetime import datetime

from schedulerApp.db import get_db
from schedulerApp.util import convert_datetime_to_user_tz

def find_dates_in_common(member_responses):
    '''go through member responses and find the time slots compatable with 
    all members who have so far responded'''
    # member_responses = [
    #   {
    #     'name': 'name',
    #     'answered': True/False
    #     'avail_slots: [
    #        {
    #          'start_time': 'MM/DD/YYYY hh:mm[AM/PM]'
    #          'end_time': 'MM/DD/YYYY hh:mm[AM/PM]'
    #        },
    #        {...}
    #      ]        
    #   },
    #   {...}
    # ]

    #get all of the availability slots that have been created
    all_avail_slots = []
    for response in member_responses:
        if response['answered'] == True:
            all_avail_slots.append(response['avail_slots'])
    
    # if at least two members have not responded return an empty list
    if len(all_avail_slots) < 2:
        return []
    
    # NOTE: The current algorithm has four for-loops and is obviously an innefficient
    # process. Because there are only intended to be up to around 10 members in an 
    # organization and up to around 10 responses from each member, I don't see this 
    # inefficiency as being a problem. Even so, a more elegant solution, assuming one 
    # exists, should be found.

    dates_in_common = []
     
    # loop through dates for first member of the organization
    for outer_slot in all_avail_slots[0]:
        # get start and end dates for the outer slot
        start_time = datetime.strptime(outer_slot['start_time'], "%m/%d/%Y %I:%M%p") 
        end_time = datetime.strptime(outer_slot['end_time'], "%m/%d/%Y %I:%M%p") 

        # because there can be multiple good slots in a given member response,
        # we need to make a list to append to and loop through
        outer_potential_times = []
        initial_outer_slot = {
            'start_time': start_time, 
            'end_time': end_time 
        }
        outer_potential_times.append(initial_outer_slot)

        # loop through the answers for the remaining members
        for member_response in all_avail_slots[1:]:
            # a list to save all good times for this member response 
            inner_potential_times = []
            # loop through each avail slot in the member_response
            for inner_slot in member_response:
                # loop through the outer potential times
                for potential_time in outer_potential_times:
                    green_light = False # determine if a good slot has been found
                    # get the datetime objects to compare to potential_time
                    compared_start_time = datetime.strptime(inner_slot['start_time'], "%m/%d/%Y %I:%M%p") 
                    compared_end_time = datetime.strptime(inner_slot['end_time'], "%m/%d/%Y %I:%M%p") 

                    # potential start and end times will be adjusted 
                    # according to the current avail slot
                    outer_start_time = potential_time['start_time'] 
                    outer_end_time = potential_time['end_time'] 

                    # compared_start_time is in the desired window, change start_time
                    if compared_start_time >= outer_start_time and compared_start_time < outer_end_time:
                        green_light = True
                        outer_start_time = compared_start_time

                    # compared_end_time is in the desired window, change end_time
                    if compared_end_time > outer_start_time and compared_end_time <= outer_end_time:
                        green_light = True
                        outer_end_time = compared_end_time
                    
                    # slot is compatable but start and end times do not change
                    if compared_start_time < outer_start_time and compared_end_time > outer_end_time:
                        green_light = True
                    
                    # if a good slot is found append it to inner_potential times
                    if green_light == True:
                        new_slot = {
                            'start_time': outer_start_time,
                            'end_time': outer_end_time
                        }
                        inner_potential_times.append(new_slot)
            
            # save all potential times found for this member response in the outer loop
            outer_potential_times = inner_potential_times

        # all of the times here are good, convert them to dict objects 
        # and append them to dates_in_common
        for time in outer_potential_times:
            good_date = {}
            good_date['start_time'] = time['start_time'].strftime("%-m/%-d/%Y %-I:%M%p")
            good_date['end_time'] = time['end_time'].strftime("%-m/%-d/%Y %-I:%M%p")
            dates_in_common.append(good_date)

    return dates_in_common

def get_member_orgs(member_id):
    '''create a lis of dicts with information from all of the organizations a member
    belongs to to be displayed on the home page. Each dict contains the keys
    'org_name' and 'org_id' '''

    db = get_db()
    cur = db.cursor()

    cur.execute(
        '''
        SELECT 
        organization.org_name, 
        organization.org_id 
        FROM organization 
        WHERE organization.org_id 
        IN (
            SELECT roster.org_id FROM roster WHERE member_id = %s
        )
        ''', 
        (member_id,)
    )
    orgs_from_db = cur.fetchall()

    orgs = []

    for o in orgs_from_db:
        org = {}

        org['org_name'] = o[0]
        org['org_id'] = o[1]  

        orgs.append(org)
    
    return orgs

def get_member_booked_dates(member_id):
    '''create a list of dicts with information from all of the booked dates for a member
    to be displayed of the home page of that member. Each dict contains the keys
    'booked_date_name, 'start_time', 'end_time', and 'timezone' get'''

    db = get_db()
    cur = db.cursor()

    cur.execute(
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
            WHERE roster.member_id = %s
        )
        ''',
        (member_id,)
    )

    member_booked_dates_from_db = cur.fetchall() 

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

def get_org_info(org_id):
    '''create a dict with keys org_id and org_name'''
    db = get_db()
    cur = db.cursor()

    cur.execute(
        '''SELECT organization.org_id, organization.org_name 
        FROM organization WHERE org_id = %s''',
        (org_id,)
    )

    org_from_db = cur.fetchone()

    org = {}
    org['org_id'] = org_from_db[0]
    org['org_name'] = org_from_db[1]

    return org

def get_roster(org_id):
    '''get a list of all member_id's associated with an organization'''
    db = get_db()
    cur = db.cursor()
    
    #TODO: add member_id to this and make a dict
    cur.execute(
        '''
        SELECT member.username, member.member_id
        FROM member
        WHERE member.member_id 
        IN(
            SELECT roster.member_id
            FROM roster
            WHERE roster.org_id = %s
        )
        ''',
        (org_id,)
    )

    roster_from_db = cur.fetchall()

    roster = []

    for r in roster_from_db:
        member = {}
        member['username'] = r[0]
        member['member_id'] = r[1]
        roster.append(member)
    return roster

def get_org_avail_requests(org_id):
    '''create a list of dicts containing information from all of the 
    availability requests associated with a particular organization to be displayed
    on the organization page. Each dict contains the keys 'avail_request_id',
    'avail_request_name', 'completed' and 'members_not_answered' '''
    db = get_db()
    cur = db.cursor()

    # get the desired fields from all 
    # availability requests associated with an organization
    cur.execute(
        '''
        SELECT 
        availability_request.avail_request_id,
        availability_request.avail_request_name,
        availability_request.completed
        FROM availability_request
        WHERE availability_request.org_id = %s
        ''',
        (org_id,)
    )

    org_avail_requests_from_db = cur.fetchall()

    org_avail_requests = []

    # create the dict object for each availability request and append them to the 
    # list that will be returned
    for org_avail_request in org_avail_requests_from_db:
        avail_request = {}
        avail_request['avail_request_id'] = org_avail_request[0]
        avail_request['avail_request_name'] = org_avail_request[1]
        avail_request['completed'] = org_avail_request[2]

        # get a list of all of the members who have not answered for the 
        cur.execute(
            '''
            SELECT member.username 
            FROM member 
            WHERE member.member_id 
            IN(
                SELECT member_request.member_id FROM  member_request 
                WHERE member_request.avail_request_id = %s
                AND member_request.answered = FALSE                
            )
            ''',
            (org_avail_request[0],) 
        )

        members_not_answered_from_db = cur.fetchall()

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
    cur = db.cursor()

    # get the desired fields for all 
    # booked_dates associated with an organization
    cur.execute(
        '''
        SELECT 
        booked_date.booked_date_name, 
        booked_date.booked_date_id,
        booked_date.start_time,
        booked_date.end_time,
        booked_date.timezone
        FROM booked_date
        WHERE booked_date.org_id = %s
        ''',
        (org_id,)
    )

    org_booked_dates_from_db = cur.fetchall()

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
    cur = db.cursor()

    # get desired fields for the availability request from the database
    cur.execute(
        '''
        SELECT 
        availability_request.avail_request_name, 
        availability_request.start_request,
        availability_request.end_request,
        availability_request.timezone,
        availability_request.org_id,
        availability_request.avail_request_id
        FROM availability_request
        WHERE avail_request_id = %s
        ''',
        (avail_request_id,)
    )
    
    avail_request_from_db = cur.fetchone()

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
    avail_request['avail_request_id'] = avail_request_from_db[5]

    return avail_request  

def get_avail_requests_data(member_id):
    '''Get a list of dicts containing data on all availability requests for a member 
    to be displayed on the home page for a member. Each dict contains the keys
    'avail_request_id', 'avail_request_name', 'org_name' and 'answered'.'''
    db = get_db()
    cur = db.cursor()

    # get all of the availability request id's assiciated with a member
    cur.execute(
        '''
        SELECT 
        availability_request.avail_request_id
        FROM availability_request 
        WHERE availability_request.avail_request_id 
        IN(
            SELECT avail_request_id FROM member_request WHERE member_request.member_id = %s
        )
        ''',
        (member_id, )
    )

    avail_request_ids = cur.fetchall()

    avail_requests = []

    # create a dict object for each availability request and append them 
    # to the list that will be returned
    for elem in avail_request_ids:
        avail_request_id = elem[0] #elem is a tuple

        cur.execute(
            '''
            SELECT availability_request.avail_request_name
            FROM availability_request
            WHERE availability_request.avail_request_id = %s
            ''',
            (avail_request_id,)
        )

        avail_request_name = cur.fetchone()[0]


        cur.execute(
            '''
            SELECT organization.org_name 
            FROM organization 
            WHERE organization.org_id
            IN(
                SELECT availability_request.org_id FROM availability_request 
                WHERE availability_request.avail_request_id = %s
            )
            ''',
            (avail_request_id,)
        )

        org_name = cur.fetchone()[0]

        cur.execute(
            '''
            SELECT member_request.answered 
            FROM member_request 
            WHERE member_request.avail_request_id = %s
            AND member_request.member_id = %s
            ''',
            (avail_request_id, session['member_id'])
        )

        answered = cur.fetchone()[0]

        # build the dict with relavant information for the avail request
        request_data = {}
        request_data['avail_request_id'] = avail_request_id
        request_data['avail_request_name'] = avail_request_name
        request_data['org_name'] = org_name
        request_data['answered'] = answered
        
        avail_requests.append(request_data)
    return avail_requests

def get_member_responses(avail_request_id):
    '''Build a list of dicts of all of the usernames, their answered status, 
    and the start and end times of any availability slots they have created 
    in association with a particular availability request to be displayed on 
    the availability request page and the book page.'''

    db = get_db()
    cur = db.cursor()
    members = [] 

    # get timzone of the avail request to convert avail_slot times from UTC
    cur.execute(
        '''
        SELECT availability_request.timezone
        FROM availability_request
        WHERE avail_request_id = %s
        ''',
        (avail_request_id,)
    )

    timezone = cur.fetchone()[0]

    # get each member and their answered status associated with the availability request
    cur.execute(
        '''
        SELECT member_request.member_id, member_request.answered
        FROM member_request 
        WHERE member_request.avail_request_id = %s
        ''',
        (avail_request_id, )
    )

    roster = cur.fetchall()

    for r in roster:
        member = {}

        member['member_id'] = r[0]

        #get the member's username
        cur.execute(
            '''
            SELECT member.username 
            FROM member
            WHERE member_id = %s
            ''',
            [r[0]] #member_id of user
        )

        username = cur.fetchone()

        member['username'] = username[0]

        # get any availability slots the member has created 
        # in assiciation with the availability_request
        cur.execute(
            '''
            SELECT 
            availability_slot.start_slot, 
            availability_slot.end_slot, 
            availability_slot.avail_slot_id
            FROM   availability_slot
            WHERE  availability_slot.avail_request_id = %s 
            AND availability_slot.member_id = %s
            ''',
            (avail_request_id, r[0],)
        )

        slots_from_db = cur.fetchall()

        member['answered'] = r[1] # answered status associated with member_id 

        slots = []
        
        # grab the start and end times and the avail_slot_id 
        # for each availability_slot the member has created
        for s in slots_from_db:
            slot = {}

            start_time = convert_datetime_to_user_tz(s[0], timezone)
            end_time = convert_datetime_to_user_tz(s[1], timezone)
            avail_slot_id = s[2]

            slot['start_time'] = start_time.strftime("%-m/%-d/%Y %-I:%M%p")
            slot['end_time'] = end_time.strftime("%-m/%-d/%Y %-I:%M%p")
            slot['avail_slot_id'] = avail_slot_id
            slots.append(slot)
        
        member['avail_slots'] = slots

        members.append(member)
    return members

def get_org_id_from_avail_request(avail_request_id):
    db = get_db()
    cur = db.cursor()

    cur.execute(
        '''
        SELECT availability_request.org_id 
        FROM availability_request
        WHERE availability_request.avail_request_id = %s
        ''',
        (avail_request_id,)
    )
    org_id = cur.fetchone()[0]
    return org_id