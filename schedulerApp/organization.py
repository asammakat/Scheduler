import datetime
from pytz import timezone, common_timezones

from flask import (
    Blueprint, flash, g, redirect, render_template, session, request, url_for
)
from werkzeug.exceptions import abort
from schedulerApp.auth import login_required
from schedulerApp.db import get_db

from schedulerApp.util import(
     return_date_values, 
     return_time_values, 
     return_datetime
)

from schedulerApp.validate import (
    validate_date, 
    validate_time, 
    validate_availability_request_input, 
    validate_start_and_end_input,
    check_org_membership, 
    check_avail_request_membership,
    validate_time_slot    
)

from schedulerApp.update_db import(
    insert_availability_request,
    insert_availability_slot, 
    insert_booked_date, 
    check_if_complete,
    delete_old_availability_requests_by_org,
    delete_old_booked_dates_by_org
)

from schedulerApp.query_db import(
    get_avail_request, 
    get_member_info,
    get_org_avail_requests, 
    get_org_booked_dates
)

bp = Blueprint('organization', __name__)  

@bp.route('/<int:org_id>/org_page', methods=('GET', 'POST'))
@login_required
def org_page(org_id):
    '''display organization information and allow user to create an 
    availability request'''
    db = get_db()

    # ensure that member is in the organization 
    if check_org_membership(org_id) == False:
        flash("You are not in the organization, ask the organization for the password to join")
        return redirect(url_for('index'))

    # get data from the organization
    org = db.execute(
        'SELECT * FROM organization WHERE org_id = ?',
        (org_id,)
    ).fetchone()

    roster = db.execute(
        '''
        SELECT member.username 
        FROM member
        WHERE member.member_id 
        IN(
            SELECT roster.member_id
            FROM roster
            WHERE roster.org_id = ?
        )
        ''',
        (org_id,)
    ).fetchall()

    # delete old avail_requests and booked dates
    delete_old_availability_requests_by_org(1)
    delete_old_booked_dates_by_org(1)

    # get data to be displayed
    org_avail_requests = get_org_avail_requests(org_id)
    org_booked_dates = get_org_booked_dates(org_id)

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
    return render_template(
        'organization/org_page.html/', 
        roster=roster, 
        org=org, 
        common_timezones=common_timezones,
        org_avail_requests=org_avail_requests,
        org_booked_dates=org_booked_dates
    )

@bp.route('/<int:avail_request_id>/avail_request', methods=('GET', 'POST'))
@login_required
def avail_request(avail_request_id):
    '''Display information about an availability request and allow user to add an 
       availability slot to that request'''
    db = get_db()

    # make sure the member is in the organization
    if check_avail_request_membership(avail_request_id) == False:
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
        timezone = avail_request['tz']

        error = validate_start_and_end_input(start_date, start_time, end_date, end_time)

        if error is None:
            error = validate_time_slot(
                avail_request['start'], 
                avail_request['end'], 
                start_date,
                start_time,
                end_date,
                end_time,
            )

            print("DEBUG: ", error)

        if error is None:
            insert_availability_slot(
                avail_request_id, 
                start_date, 
                start_time, 
                end_date, 
                end_time, 
                timezone
            )
            flash("Availability slot added, add another?")
            if check_if_complete(avail_request_id):
                flash("Request complete! Ready to book")
        
        else:
            flash(error)

    return render_template(
        'organization/avail_request.html/', 
        avail_request=avail_request,
        members=members,
        avail_request_id=avail_request_id
    )

@bp.route('/<int:avail_request_id>/book', methods=('GET', 'POST'))
@login_required
def book(avail_request_id):
    '''Display all of the entered avalability for an abailability request 
    and allow a user to create a booked date'''
    db = get_db()

    # ensure that the member is in the organization that has the availability request
    if check_avail_request_membership(avail_request_id) == False:
        flash("You are not in the organization that has this availability request")
        return redirect(url_for('index'))   
    
    # get the data from the database to be displayed 
    avail_request = get_avail_request(avail_request_id)
    members = get_member_info(avail_request_id)

    if request.method == 'POST':
        start_date = request.form['start_date']
        start_time = request.form['start_time']
        end_date = request.form['end_date']
        end_time = request.form['end_time']
        timezone = avail_request['tz']

        error = validate_start_and_end_input(start_date, start_time, end_date, end_time)

        if error is None:
            insert_booked_date(avail_request_id, start_date, start_time, end_date, end_time, timezone)
            flash("Date booked!")
            return redirect(url_for('index', org_id = avail_request['org_id']))
        else:
            flash(error)

    return render_template('organization/book.html', avail_request=avail_request, members=members)