from flask import (
    Blueprint, flash, g, redirect, render_template, session, request, url_for
)
from werkzeug.exceptions import abort

from schedulerApp.auth import login_required
from schedulerApp.db import get_db

from schedulerApp.query_db import get_avail_requests_data, get_member_booked_dates, get_member_orgs
from schedulerApp.update_db import (
    update_availability_requests_by_member, update_booked_dates_by_member
)

bp = Blueprint('member', __name__)

@bp.route('/')
def index():
    '''display the organizations and availability requests associated with a member
    if a member is logged in and allows for registration and member login if 
    a member is not logged in'''
    db = get_db()
    orgs = None
    avail_requests = None
    member_id = session.get('member_id')
    booked_dates = None
    if member_id is not None:

        # delete old avail requests and booked dates and get session data
        update_availability_requests_by_member(member_id)
        update_booked_dates_by_member(member_id)

        session['orgs'] = get_member_orgs(member_id)
        session.modified = True

    return render_template(
        'member/index.html', 
    )

