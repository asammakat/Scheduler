import pytest

from flask import g, session
from schedulerApp.db import get_db

def test_org_page(auth, client, app):
    auth.login()
    assert client.get('/1/org_page').status_code == 200

    auth.make_avail_request()

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM availability_request WHERE avail_request_name ='testAR'", 
        ).fetchone() is not None

@pytest.mark.parametrize(('avail_request_name', 'start_date', 'start_time', 'end_date', 'end_time', 'tz', 'message'),(
    ('', '1/1/2030', '1:30a', '1/1/2030', '2:00p', 'UTC', b"A name is required"),
    ('testAR', '', '1:30a', '1/1/2030', '2:00p', 'UTC', b"There was a problem with your start date input"),
    ('testAR','1/1/2030', '', '1/1/2030', '2:00p', 'UTC', b"There was a problem with your start time input"),
    ('testAR','1/1/2030', '1:30a', '', '2:00p', 'UTC', b"There was a problem with your end date input"),
    ('testAR','1/1/2030', '1:30a', '1/1/2030', '', 'UTC', b"There was a problem with your end time input"),
    ('testAR','1/1/2030', '1:30a', '1/1/2030', '2:00p', '', b"Timezone is required")
))
def test_org_page_validate_input(avail_request_name, start_date, start_time, end_date, end_time, tz, message, auth):
    auth.login()
    response = auth.make_avail_request(
        avail_request_name=avail_request_name,
        start_date=start_date, 
        start_time=start_time, 
        end_date=end_date, 
        end_time=end_time, 
        tz=tz
    )
    assert message in response.data
