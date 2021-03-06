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
    update_availability_requests_by_org,
    update_booked_dates_by_org, 
    delete_availability_request,
    delete_booked_date,
    delete_availability_slot,
    remove_from_org
)

from schedulerApp.query_db import(
    get_avail_request, 
    get_member_responses,
    get_org_avail_requests, 
    get_org_booked_dates,
    get_org_info,
    get_roster,
    find_dates_in_common,
    get_org_id_from_avail_request    
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
    session['active_org'] = get_org_info(org_id)
    session['roster'] = get_roster(org_id)

    # delete old avail_requests and booked dates and get session data
    update_availability_requests_by_org(org_id)
    update_booked_dates_by_org(org_id)
    # NOTE: At the moment grabbing this information is redundant because all of 
    # the availability requests for this organization is stored in 
    # session['availability_request'] and session['booked_dates']. However we are 
    # getting this information seperately both because it is organizationally consistent 
    # with the organization of the app and because in the future we might have a scenario 
    # where we want there to be availability requests and booked dates that 
    # do not include all members of an organization    

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
        common_timezones=common_timezones,
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

    session['active_avail_request'] = get_avail_request(avail_request_id)

    if 'active_org' not in session.keys():
        org_id = get_org_id_from_avail_request(avail_request_id)
        session['active_org'] = get_org_info(org_id)
        session['roster'] = get_roster(org_id)        

    # get list of dicts containing each member in the organization's information
    # regarding the availabiity request 
    # member_responses = [
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
    session['member_responses'] = get_member_responses(avail_request_id)

    # find the dates in common for the members who have responded to the avail request
    session['dates_in_common'] = find_dates_in_common(session['member_responses'])
    session.modified = True      

    if request.method == 'POST':
        start_date = request.form['start_date']
        start_time = request.form['start_time']
        end_date = request.form['end_date']
        end_time = request.form['end_time']
        timezone = session['active_avail_request']['tz']

        error = validate_start_and_end_input(start_date, start_time, end_date, end_time)

        if error is None:
            error = validate_time_slot(
                session['active_avail_request']['start'], 
                session['active_avail_request']['end'], 
                start_date,
                start_time,
                end_date,
                end_time,
            )

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
        avail_request_id=avail_request_id
    )

@bp.route('/<int:avail_request_id>/delete_avail_request')
@login_required
def delete_avail_request(avail_request_id): #TODO: rename to 'delete_avail_request_page'
    '''Allow user to delete an availability request'''
    delete_availability_request(avail_request_id)
    flash("availability request deleted")
    # return user to the org page
    return redirect(url_for('organization.org_page', org_id=session['active_org']['org_id'] ))

@bp.route('/<int:avail_slot_id>/delete_avail_slot')
@login_required
def delete_avail_slot(avail_slot_id):
    '''Allow user to delete an availability slot'''
    delete_availability_slot(avail_slot_id)
    flash("availability slot deleted")
    # return user to the avail_request page
    return redirect(url_for('organization.avail_request', avail_request_id=session['active_avail_request']['avail_request_id']))


@bp.route('/<int:booked_date_id>/delete_booked_date')
@login_required
def delete_booked_date_page(booked_date_id):
    '''Allow user to delete a booked date'''
    delete_booked_date(booked_date_id)
    flash("booked date deleted")
    # return user to the org page 
    return redirect(url_for('organization.org_page', org_id=session['active_org']['org_id'] ))

@bp.route('/<int:member_id>/<int:org_id>/leave_org')
@login_required
def leave_org(member_id, org_id):
    '''Allow a member to be leave an organization'''
    remove_from_org(member_id, org_id)
    flash("member removed from roster")
    # return to the home page
    return redirect('/')

@bp.route('/<int:member_id>/<int:org_id>/drop_from_org')
@login_required
def drop_from_org(member_id, org_id):
    '''Allow a member to be dropped from an organization'''
    remove_from_org(member_id, org_id)
    flash("member removed from roster")
    # return to the home page
    return redirect(url_for('organization.org_page',  org_id=session['active_org']['org_id']))    
    

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
    if 'active_avail_request' not in session.keys():
        session['active_avail_request'] = get_avail_request(avail_request_id)
        session['member_responses'] = get_member_responses(avail_request_id)  

    if request.method == 'POST':
        start_date = request.form['start_date']
        start_time = request.form['start_time']
        end_date = request.form['end_date']
        end_time = request.form['end_time']
        timezone = session['active_avail_request']['tz']

        error = validate_start_and_end_input(start_date, start_time, end_date, end_time)

        if error is None:
            insert_booked_date(avail_request_id, start_date, start_time, end_date, end_time, timezone)
            flash("Date booked!")
            return redirect(url_for('index', org_id = session['active_avail_request']['org_id']))
        else:
            flash(error)

    return render_template('organization/book.html', avail_request_id=avail_request_id)

