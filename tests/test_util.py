import pytest

from schedulerApp.util import *

def test_return_date_values():
    test_var = return_date_values('12/12/2030')
    assert test_var['year'] == 2030
    assert test_var['month'] == 12
    assert test_var['day'] == 12

def test_return_time_values():
    test_var = return_time_values('1:00a') 
    assert test_var['hour'] == 1
    assert test_var['minute'] == 0

    test_var = return_time_values('1:01p')
    assert test_var['hour'] == 13
    assert test_var['minute'] == 1

    test_var = return_time_values('12:30p')
    assert test_var['hour'] == 12
    assert test_var['minute'] == 30

    test_var = return_time_values('12:01a')
    assert test_var['hour'] == 0
    assert test_var['minute'] == 1

def test_return_datetime():
    #TODO: test more timezones from across the world and strange timezone situations

    test_datetime = return_datetime('1/1/2030', '6:00p', 'UTC')
    assert type(test_datetime) == datetime.datetime
    assert test_datetime.tzinfo == None
    assert test_datetime.hour == 18

    test_datetime = return_datetime('6/1/2030', '6:00p', 'America/Los_Angeles')
    assert type(test_datetime) == datetime.datetime
    assert test_datetime.tzinfo == None
    assert test_datetime.hour == 1
    assert test_datetime.day == 2 

    test_datetime = return_datetime('1/1/2030', '6:00p', 'America/Los_Angeles')
    assert type(test_datetime) == datetime.datetime
    assert test_datetime.tzinfo == None
    assert test_datetime.hour == 2
    assert test_datetime.day == 2 

    test_datetime = return_datetime('6/1/2030', '6:00p', 'America/Chicago')
    assert type(test_datetime) == datetime.datetime
    assert test_datetime.tzinfo == None
    assert test_datetime.hour == 23
    assert test_datetime.day == 1 

    test_datetime = return_datetime('1/1/2030', '6:00p', 'America/Chicago')
    assert type(test_datetime) == datetime.datetime
    assert test_datetime.tzinfo == None
    assert test_datetime.hour == 0
    assert test_datetime.day == 2


