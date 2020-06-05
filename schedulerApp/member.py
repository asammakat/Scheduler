from flask import (
    Blueprint, flash, g, redirect, render_template, session, request, url_for
)
from werkzeug.exceptions import abort

from schedulerApp.auth import login_required
from schedulerApp.db import get_db
from schedulerApp.helper import get_avail_requests_data

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
    if member_id is not None:
        orgs = db.execute(
            'SELECT organization.org_name, organization.org_id FROM organization WHERE organization.org_id IN (SELECT roster.org_id FROM roster WHERE member_id = ?)', 
            (member_id,)
        ).fetchall() 

        avail_requests = get_avail_requests_data(member_id)

    return render_template('member/index.html', orgs=orgs, avail_requests=avail_requests)

