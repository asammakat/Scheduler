import pytest

from flask import g, session
from schedulerApp.db import get_db
from schedulerApp.helper import * 

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

def test_validate_time():
    for i in range(1, 13):
        # check that all valid times return True
        for j in range(10):
            test_string_am = str(i) + ':0' + str(j) + 'a'
            test_string_pm = str(i) + ':0' + str(j) + 'p'
            assert validate_time(test_string_am) == True
            assert validate_time(test_string_pm) == True

            # times without a trailing 'a' or 'p' should return False
            test_string_am = str(i) + ':0' + str(j) 
            test_string_pm = str(i) + ':0' + str(j)
            assert validate_time(test_string_am) == False
            assert validate_time(test_string_pm) == False
        for k in range(10,60):
            test_string_am = str(i) + ':' + str(k) + 'a'
            test_string_pm = str(i) + ':' + str(k) + 'p'
            assert validate_time(test_string_am) == True
            assert validate_time(test_string_pm) == True

            test_string_am = str(i) + ':' + str(k) 
            test_string_pm = str(i) + ':' + str(k) 
            assert validate_time(test_string_am) == False
            assert validate_time(test_string_pm) == False

        # test other situations that should return False
        assert validate_time('') == False
        assert validate_time('00:00a') == False
        assert validate_time('99:99p') == False
        assert validate_time('120:00a') == False
        assert validate_time('12:001') == False
        assert validate_time('12:100') == False

def test_validate_date():
    months_with_31 = [1,3,5,7,8,10,12]
    months_with_30 = [4,6,9,11]

    # check that minimum and maximum values for dates return True and or of range values return False
    for i in range(1, 13):
        test_string = str(i) + '/' + '1' + '/' + '2030'
        assert validate_date(test_string) == True
    
        if i in months_with_31:
            test_string = str(i) + '/' + '31' + '/' + '2030'
            assert validate_date(test_string) == True 
            test_string = str(i) + '/' + '32' + '/' + '2030'
            assert validate_date(test_string) == False
        
        elif i in months_with_30:
            test_string = str(i) + '/' + '30' + '/' + '2030'
            assert validate_date(test_string) == True 
            test_string = str(i) + '/' + '31' + '/' + '2030'
            assert validate_date(test_string) == False
        else:
            test_string = str(i) + '/' + '29' + '/' + '2030'
            assert validate_date(test_string) == True 
            test_string = str(i) + '/' + '30' + '/' + '2030'
            assert validate_date(test_string) == False
        
        
    #check that year values from 1900 t0 2999 return True
    for i in range(1900, 3000):
        test_string = '1/1/' + str(i)
        assert validate_date(test_string) == True
    
    #test other situations that should return False
    assert validate_date('') == False
    assert validate_date('12-12-2030') == False
    assert validate_date('0/1/2030') == False
    assert validate_date('1/0/2030') == False
    assert validate_date('1/1/0') == False
    assert validate_date('/1/2030') == False
    assert validate_date('1//2030') == False
    assert validate_date('1/1/') == False

def test_return_datetime():
    test_datetime = return_datetime('1/1/2030', '6:00p')
    assert type(test_datetime) == datetime.datetime