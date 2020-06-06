import re
import datetime
from flask import session

from schedulerApp.db import get_db

def return_date_values(date):
    '''take a formatted string (mm/dd/yyyy) and return a dict with month, day, and year info'''
    #split the string and grab integer values
    date = date.split('/')
    month = int(date[0])
    day = int(date[1])
    year = int(date[2])

    #create a dict to be returned
    result = {}
    result['month'] = month
    result['day'] = day
    result['year'] = year
    return result

def return_time_values(time):
    ''' take a formatted string (hh:mm[a/p]) and return a dict with the hour and minute info.
        use the last character of the formatted string to perform am/pm conversions for the
        hour field'''
    #split the string and grab integer values
    am_or_pm = time[-1] # last char of time is a or p
    time = time.split(':')
    hour = int(time[0])
    minute = int(time[1][:-1]) # get rid of last char

    # am/pm conversion into 24hr time
    if am_or_pm == "p":
        #make adjustment from 1:00 pm - 11:59pm
        if hour != 12:           
            hour = hour + 12 
    else:
        #make adjustment from 12:00am - 12:59am
        if hour == 12:
            hour = 0

    # create a dict to be returned
    result = {}
    result['hour'] = hour
    result['minute'] = minute 
    return result

def validate_time(time):
    '''Check that user has entered time in the correct format'''
    pattern = re.compile(r"^(0?[1-9]|1[0-2]):[0-5][0-9][a|p]$")
    if pattern.fullmatch(time):
        return True
    else:
        return False

def validate_date(date):
    '''Check that user has entered date in the correct format'''
    pattern = re.compile(r"^(0?[1-9]|1[012])/(0?[1-9]|[12][0-9]|3[01])/(19|2\d)\d\d$")
    if pattern.fullmatch(date):

        splitDate = date.split("/")
        month = int(splitDate[0])
        day = int(splitDate[1])
        if month == 4 or month == 6 or month == 9 or month == 11: 
           if(day > 30):
               return False
        if month == 2:
            if day > 29:
                return False
        return True
    else:
        return False   

def validate_availability_request_input(
    tz, 
    avail_request_name, 
    start_date, 
    start_time, 
    end_date, 
    end_time
):
    '''Validate the user input to create an availability request'''
    if avail_request_name == '':
        error = "A name is required"
    elif not validate_date(start_date):
        error = "There was a problem with your start date input"
    elif not validate_time(start_time):
        error = "There was a problem with your start time input"
    elif not validate_date(end_date):
        error = "There was a problem with your end date input"
    elif not validate_time(end_time):
        error = "There was a problem with your end time input"
    elif tz == '':
        error = "Timezone is required"
    else:
        error = None
    return error    

def validate_start_and_end_input(start_date, start_time, end_date, end_time):
    '''Validate the user input to create an availability slot'''
    if not validate_date(start_date):
        error = "There was a problem with your start date input"
    elif not validate_time(start_time):
        error = "There was a problem with your start time input"
    elif not validate_date(end_date):
        error = "There was a problem with your end date input"
    elif not validate_time(end_time):
        error = "There was a problem with your end time input"   
    else:
        error = None 
    return error    



def check_org_membership(org_id):
    db = get_db()
    # ensure that member is in the organization 
    if db.execute(
        'SELECT * FROM roster WHERE org_id = ? AND member_id = ?',
        (org_id, session['member_id'],)
    ).fetchone() is None:
        return False
    else:
        return True

def check_avail_request_membership(avail_request_id):
    db = get_db()
    if db.execute(
        'SELECT * FROM member_request WHERE avail_request_id = ? AND member_id = ?',
        (avail_request_id, session['member_id'],)
    ).fetchone() is None:
        return False
    else:
        return True
    
def return_datetime(date_string, time_string):
    ''' take a formatted date string and a formatted time string and return
    a datetime object from them '''
    #dates are returned as a dict with 'day', 'month' and 'year' keys
    #times are be returned as a dict with 'hour' and 'minute' keys
    date = return_date_values(date_string)
    time = return_time_values(time_string) 

    result = datetime.datetime(
        date['year'], date['month'], date['day'],
        time['hour'], time['minute']
    )

    return result

def insert_booked_date(avail_request_id, start_date, start_time, end_date, end_time):
    db = get_db()

    start_book = return_datetime(start_date, start_time)
    end_book = return_datetime(end_date, end_time)    

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

    db.execute(
        '''INSERT INTO booked_date(
            booked_date_name, start_time, end_time, timezone, org_id, avail_request_id
        ) VALUES (?,?,?,?,?,?)''',
        (name, start_book, end_book, tz, org_id, avail_request_id,)
    )

    db.execute(
        '''
        UPDATE availability_request SET completed = TRUE WHERE avail_request_id = ?
        ''',
        (avail_request_id,)
    )
    db.commit()

def insert_availability_slot(avail_request_id, start_date, start_time, end_date, end_time):
    '''insert an availability slot into the database'''

    db = get_db()
    # get datetime objects for start and end
    start_slot = return_datetime(start_date, start_time)
    end_slot = return_datetime(end_date, end_time)

    # insert new availability slot into the database
    db.execute(
        '''INSERT INTO availability_slot(
            start_slot, end_slot, avail_request_id, member_id
        ) VALUES (?,?,?,?)''',
        (start_slot, end_slot, avail_request_id, session['member_id'],)
    )

    # set the answer field in member_request to TRUE
    db.execute(
        ''' UPDATE member_request SET answered = TRUE WHERE member_id = ? AND avail_request_id = ? ''',
        (session['member_id'], avail_request_id,)
    )
    db.commit()

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
    start_request = return_datetime(start_date, start_time)
    end_request = return_datetime(end_date, end_time)

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

def get_avail_request(avail_request_id):
    '''get information for an availability request from the database 
    to display on the avail_request page'''
    db = get_db()
    # get information for the availability request from the database
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
    avail_request['name'] = avail_request_from_db[0]
    avail_request['start'] = avail_request_from_db[1].strftime("%-m/%-d/%Y %-I:%M%p")
    avail_request['end'] = avail_request_from_db[2].strftime("%-m/%-d/%Y %-I:%M%p")
    avail_request['tz'] = avail_request_from_db[3] 
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
    '''Build a list of dicts of all of the usernames, their answered status, and the start and end times of
    any availability slots they have created in association with a particular availability request. 
    roster is a list of '''
    db = get_db()
    members = []

    # get each member and their answered status associated with the availability request
    roster = db.execute(
        '''
        SELECT member_request.member_id, member_request.answered
        FROM member_request where member_request.avail_request_id = ?
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
            slot['start_time'] = s[0].strftime("%-m/%-d/%Y %-I:%M%p")
            slot['end_time'] = s[1].strftime("%-m/%-d/%Y %-I:%M%p")
            slots.append(slot)
        
        member['avail_slots'] = slots

        members.append(member)
    return members
