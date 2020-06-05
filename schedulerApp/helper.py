import re
import datetime
from schedulerApp.db import get_db

def return_date_values(date):
    date = date.split('/')
    month = int(date[0])
    day = int(date[1])
    year = int(date[2])
    result = [month, day, year]
    return result

def return_time_values(time):
    ''' take a formatted string (hh:mm[a/p]) and return a dict with the hour/minute info.
        use the last character of the formatted string to perform am/pm conversions for the
        hour field'''
    am_or_pm = time[-1] # last char of time is a or p
    time = time.split(':')
    print(time)
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

    result = [hour, minute]  
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
    
def return_datetime(date_string, time_string):
    #dates are returned as a list [m,d,Y]
    #times are be returned as a list [h,m]
    date = return_date_values(date_string)
    time = return_time_values(time_string) 

    result = datetime.datetime(
        date[2], date[0], date[1],
        time[0], time[1]
    )

    return result

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