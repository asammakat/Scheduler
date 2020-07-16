import re
from datetime import datetime

from flask import session
from schedulerApp.db import get_db
from schedulerApp.util import return_datetime



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
    elif not validate_start_before_end(start_date, start_time, end_date, end_time):
        error = "Start must be before end"
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
    elif not validate_start_before_end(start_date, start_time, end_date, end_time):
        error = "Start must be before end" 
    else:
        error = None 
    return error    

def validate_time_slot(
    avail_request_start, #formatted datetime string
    avail_request_end,   #formatted datetime string
    start_slot_date, 
    start_slot_time, 
    end_slot_date, 
    end_slot_time 
):
    #get datetimes for the start and end of the availability_slot
    start_slot_datetime = return_datetime(start_slot_date, start_slot_time)
    end_slot_datetime = return_datetime(end_slot_date, end_slot_time)

    #get datetimes for the start and end of the the availability request
    avail_request_start_datetime = datetime.strptime(avail_request_start, "%m/%d/%Y %I:%M%p")
    avail_request_end_datetime = datetime.strptime(avail_request_end, "%m/%d/%Y %I:%M%p")

    if start_slot_datetime < avail_request_start_datetime:
        return "availability slot cannot start before the availability request"
    elif end_slot_datetime > avail_request_end_datetime:
        return "avaiability slot cannot end after the availability request"
    else:
        return None
    
def validate_start_before_end(start_date, start_time, end_date, end_time):
    start_datetime = return_datetime(start_date, start_time)
    end_datetme = return_datetime(end_date, end_time)

    if end_datetme < start_datetime:
        return False
    else:
        return True

def check_org_membership(org_id):
    '''check if a member is in an organization'''
    db = get_db()
    cur = db.cursor()
    cur.execute(
        'SELECT * FROM roster WHERE org_id = %s AND member_id = %s',
        (org_id, session['member_id'],)
    )
    result = cur.fetchone()
    if result is None: #member not contained in roster
        return False
    else:
        return True
    
def check_avail_request_membership(avail_request_id):
    '''check if a user is associated with a partiular availability request'''
    db = get_db()
    cur = db.cursor()
    cur.execute(
        'SELECT * FROM member_request WHERE avail_request_id = %s AND member_id = %s',
        (avail_request_id, session['member_id'],)
    )
    result = cur.fetchone()

    if result is None:
        return False
    else:
        return True