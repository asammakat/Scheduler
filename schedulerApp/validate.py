import re

from flask import session
from schedulerApp.db import get_db



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
    '''check if a member is in an organization'''
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
    '''check if a user is associated with a partiular availability request'''
    db = get_db()
    if db.execute(
        'SELECT * FROM member_request WHERE avail_request_id = ? AND member_id = ?',
        (avail_request_id, session['member_id'],)
    ).fetchone() is None:
        return False
    else:
        return True