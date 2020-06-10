import re
import datetime

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