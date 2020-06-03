from flask import (
    Blueprint, flash, g, redirect, render_template, session, request, url_for
)
from werkzeug.exceptions import abort

from schedulerApp.auth import login_required
from schedulerApp.db import get_db

bp = Blueprint('member', __name__)

@bp.route('/')
def index():
    db = get_db()
    orgs = None
    avail_requests = None
    member_id = session.get('member_id')
    if member_id is not None:
        orgs = db.execute(
            'SELECT organization.org_name, organization.org_id FROM organization WHERE organization.org_id IN (SELECT roster.org_id FROM roster WHERE member_id = ?)', 
            (member_id,)
        ).fetchall()

        avail_requests = db.execute(
            '''SELECT 
               availability_request.avail_request_id, availability_request.avail_request_name, organization.org_name 
               FROM availability_request 
               JOIN organization 
               ON availability_request.org_id = organization.org_id 
               WHERE availability_request.avail_request_id 
               IN (
                   SELECT avail_request_id FROM member_request WHERE member_id = ?
                   )''',
            (member_id,)
        ).fetchall()

    return render_template('member/index.html', orgs=orgs, avail_requests=avail_requests)




