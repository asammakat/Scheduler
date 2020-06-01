import datetime
from pytz import timezone, common_timezones

from flask import (
    Blueprint, flash, g, redirect, render_template, session, request, url_for
)
from werkzeug.exceptions import abort

from schedulerApp.auth import login_required
from schedulerApp.db import get_db
from schedulerApp.helper import return_date_values, return_time_values, validate_date, validate_time


bp = Blueprint('organization', __name__) 

@bp.route('/<int:org_id>/org_page', methods=('GET', 'POST'))
@login_required
def org_page(org_id):
    #TODO: make it so that you cannot see orgs that you do not belong to(currently can type org id into the browser)

    db = get_db()
    org = db.execute(
        'SELECT * FROM organization WHERE org_id = ?',
        (org_id,)
    ).fetchone()
    if request.method == 'POST':

        tz = request.form["tz"]
        avail_request_name = request.form['avail_request_name']
        start_date_string = request.form['start_date']
        start_time_string = request.form['start_time']
        end_date_string = request.form['end_date']
        end_time_string = request.form['end_time']

        flash(f'''Availability Request {avail_request_name} from {start_date_string}
                starting at {start_time_string} to {end_date_string} ending at 
                {end_time_string} in {tz} being created...''')
            
        error = None
            
        # validate input
        if avail_request_name == '':
            error = "A name is required"
        elif not validate_date(start_date_string):
            error = "There was a problem with your start date input"
        elif not validate_time(start_time_string):
            error = "There was a problem with your start time input"
        elif not validate_date(end_date_string):
            error = "There was a problem with your end date input"
        elif not validate_time(end_time_string):
            error = "There was a problem with your end time input"
        elif tz == '':
            error = "Timezone is required"
    
        if error is None:
            #get integer values from the user entered string
            #dates will be returned as a list [m,d,Y]
            #times will be returned as a list [h,m]
            start_date = return_date_values(start_date_string)
            start_time = return_time_values(start_time_string)
            end_date = return_date_values(end_date_string)
            end_time = return_time_values(end_time_string)

            #create datetimes for start and end
            start_request = datetime.datetime(
                start_date[2], start_date[0], start_date[1],
                start_time[0], start_time[1]
            )

            end_request = datetime.datetime(
                end_date[2], end_date[0], end_date[1],
                end_time[0], end_time[1]
            )

            db.execute(
                ''' INSERT INTO availability_request 
                (avail_request_name, start_request, end_request, 
                timezone, org_id, completed) VALUES (?, ?, ?, ?, ?, ?)''',
                (avail_request_name, start_request, end_request, tz, org_id, False)
            )

            member_id = session.get('member_id')
            avail_request_id = db.execute('SELECT avail_request_id FROM availability_request WHERE avail_request_name = ?', (avail_request_name,)).fetchone()

            db.execute(
                'INSERT INTO member_request (member_id, avail_request_id, answered) VALUES (?,?,?)',
                (member_id, avail_request_id[0], False)
            )
            db.commit()

        flash(error)
    return render_template('organization/org_page.html', org=org, common_timezones=common_timezones)