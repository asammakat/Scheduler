import datetime
from pytz import timezone, common_timezones

from flask import (
    Blueprint, flash, g, redirect, render_template, session, request, url_for
)
from werkzeug.exceptions import abort
from schedulerApp.auth import login_required
from schedulerApp.db import get_db
from schedulerApp.helper import return_date_values, return_time_values, validate_date, validate_time, return_datetime

bp = Blueprint('organization', __name__) 

@bp.route('/<int:org_id>/org_page', methods=('GET', 'POST'))
@login_required
def org_page(org_id):    

    db = get_db()

    # ensure that member is in the organization 
    if db.execute(
        'SELECT * FROM roster WHERE org_id = ? AND member_id = ?',
        (org_id, session['member_id'],)
    ).fetchone() is None:
        flash("You are not in the organization, ask the organization for the password to join")
        return redirect(url_for('index'))

    # get data from the organization
    org = db.execute(
        'SELECT * FROM organization WHERE org_id = ?',
        (org_id,)
    ).fetchone()

    if request.method == 'POST':

        tz = request.form["tz"]
        avail_request_name = request.form['avail_request_name']
        start_date = request.form['start_date']
        start_time = request.form['start_time']
        end_date = request.form['end_date']
        end_time = request.form['end_time']

        flash(f'''Availability Request {avail_request_name} from {start_date}
                starting at {start_time} to {end_date} ending at 
                {end_time} in {tz} being created...''')
            
        error = None
            
        # validate input
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
    
        if error is None:

            start_request = return_datetime(start_date, start_time)
            end_request = return_datetime(end_date, end_time)

            db.execute(
                ''' INSERT INTO availability_request 
                (avail_request_name, start_request, end_request, 
                timezone, org_id, completed) VALUES (?, ?, ?, ?, ?, ?)''',
                (avail_request_name, start_request, end_request, tz, org_id, False)
            )

            member_id = session.get('member_id')
            avail_request_id = db.execute(
                'SELECT avail_request_id FROM availability_request WHERE avail_request_name = ?', 
                (avail_request_name,)).fetchone()

            db.execute(
                'INSERT INTO member_request (member_id, avail_request_id, answered) VALUES (?,?,?)',
                (member_id, avail_request_id[0], False)
            )
            db.commit()

        else:
            flash(error)

    return render_template('organization/org_page.html/', org=org, common_timezones=common_timezones)


@bp.route('/<int:avail_request_id>/avail_request', methods=('GET', 'POST'))
def avail_request(avail_request_id):
    db = get_db()

    if db.execute(
        'SELECT * FROM member_request WHERE avail_request_id = ? AND member_id = ?',
        (avail_request_id, session['member_id'],)
    ).fetchone() is None:
        flash("You are not in the organization that has the availability request")
        return redirect(url_for('index'))


    avail_request = db.execute(
        '''SELECT 
           availability_request.avail_request_name, 
           availability_request.start_request,
           availability_request.end_request,
           availability_request.timezone
           FROM availability_request
           WHERE avail_request_id = ?''',
           (avail_request_id,)
        ).fetchone()
    
    avail_request_name = avail_request[0]
    avail_request_start = avail_request[1].strftime("%-m/%-d/%Y %-I:%M%p")#convert datetime to formatted string
    avail_request_end = avail_request[2].strftime("%-m/%-d/%Y %-I:%M%p")
    avail_request_tz = avail_request[3]

    if request.method == 'POST':
        start_date = request.form['start_date']
        start_time = request.form['start_time']
        end_date = request.form['end_date']
        end_time = request.form['end_time']

        error = None

        if not validate_date(start_date):
            error = "There was a problem with your start date input"
        elif not validate_time(start_time):
            error = "There was a problem with your start time input"
        elif not validate_date(end_date):
            error = "There was a problem with your end date input"
        elif not validate_time(end_time):
            error = "There was a problem with your end time input"

        if error is None:
            start_slot = return_datetime(start_date, start_time)
            end_slot = return_datetime(end_date, end_time)

            db.execute(
                '''INSERT INTO availability_slot(start_slot, end_slot, avail_request_id, member_id) VALUES (?,?,?,?)''',
                (start_slot, end_slot, avail_request_id, session['member_id'],)
            )

            db.execute(
                ''' UPDATE member_request SET answered = TRUE WHERE member_id = ? AND avail_request_id = ? ''',
                (session['member_id'], avail_request_id,)
            )
            db.commit()
            flash("Availability slot added, add another?")
        
        else:
            flash(error)

    return render_template(
        'organization/avail_request.html/', 
        avail_request_name=avail_request_name,  
        avail_request_start=avail_request_start,
        avail_request_end=avail_request_end,
        avail_request_tz=avail_request_tz
    )