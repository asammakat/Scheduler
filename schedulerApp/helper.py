import re

def return_date_values(date):
    date = date.split('/')
    month = int(date[0])
    day = int(date[1])
    year = int(date[2])
    result = [month, day, year]
    return result

def return_time_values(time):
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
    pattern = re.compile(r"^(0?[1-9]|1[0-2]):[0-5][0-9][a|p]$")
    if pattern.fullmatch(time):
        return True
    else:
        return False

def validate_date(date):
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