import datetime
from pytz import timezone, common_timezones

from flask import (
    Blueprint, flash, g, redirect, render_template, session, request, url_for
)
from werkzeug.exceptions import abort
from schedulerApp.auth import login_required
from schedulerApp.db import get_db
from schedulerApp.helper import(return_date_values, 
                                return_time_values, 
                                return_datetime,                                
                                validate_date, 
                                validate_time, 
                                validate_availability_request_input,
                                validate_availability_slot_input,                                
                                get_avail_request, 
                                get_member_info,
                                insert_availability_request,
                                insert_availability_slot)

bp = Blueprint('organization', __name__)  

@bp.route('/<int:org_id>/org_page', methods=('GET', 'POST'))
@login_required
def org_page(org_id):
    '''display organization information and allow user to create an 
    availability request'''
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
        #get availability request data from form
        tz = request.form['tz']
        avail_request_name = request.form['avail_request_name']
        start_date = request.form['start_date']
        start_time = request.form['start_time']
        end_date = request.form['end_date']
        end_time = request.form['end_time']

        flash(f'''Availability Request {avail_request_name} from {start_date}
                starting at {start_time} to {end_date} ending at 
                {end_time} in {tz} being created...''')
                        
        # validate input
        error = validate_availability_request_input(
            tz, 
            avail_request_name, 
            start_date, 
            start_time, 
            end_date, 
            end_time
        )
    
        if error is None:
            # insert the availability request into the databse
            insert_availability_request(
                org_id,
                tz, 
                avail_request_name, 
                start_date, 
                start_time, 
                end_date, 
                end_time
            )
        else:
            flash(error) 
    return render_template('organization/org_page.html/', org=org, common_timezones=common_timezones)

@bp.route('/<int:avail_request_id>/avail_request', methods=('GET', 'POST'))
def avail_request(avail_request_id):
    '''Display information about an availability request and allow user to add an 
       availability slot to that request'''
    db = get_db()

    # make sure the member is in the organization
    if db.execute(
        'SELECT * FROM member_request WHERE avail_request_id = ? AND member_id = ?',
        (avail_request_id, session['member_id'],)
    ).fetchone() is None:
        flash("You are not in the organization that has this availability request")
        return redirect(url_for('index'))   

    avail_request = get_avail_request(avail_request_id)

    # get list of dicts containing each member in the organization's information
    # regarding the availabiity request 
    # members = [
    #   {
    #     'name': 'name',
    #     'answered': True/False
    #     'avail_slots: [
    #        {
    #          'start_time': 'MM/DD/YYYY hh:mm[AM/PM]'
    #          'end_time': 'MM/DD/YYYY hh:mm[AM/PM]'
    #        },
    #        {...}
    #      ]        
    #   },
    #   {...}
    # ]
    members = get_member_info(avail_request_id)    

    if request.method == 'POST':
        start_date = request.form['start_date']
        start_time = request.form['start_time']
        end_date = request.form['end_date']
        end_time = request.form['end_time']

        error = validate_availability_slot_input(start_date, start_time, end_date, end_time)

        if error is None:
            insert_availability_slot(avail_request_id, start_date, start_time, end_date, end_time)
            flash("Availability slot added, add another?")
        
        else:
            flash(error)

    return render_template(
        'organization/avail_request.html/', 
        avail_request=avail_request,
        members=members
    )