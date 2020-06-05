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
    page_data = None
    member_id = session.get('member_id')
    if member_id is not None:
        orgs = db.execute(
            'SELECT organization.org_name, organization.org_id FROM organization WHERE organization.org_id IN (SELECT roster.org_id FROM roster WHERE member_id = ?)', 
            (member_id,)
        ).fetchall() 

        # grab the current availability requests, the organizations they belong to,
        # and the answered status for the current member  

        #need avail_request_id, avail_request_name, org_name, answered
        avail_request_ids = db.execute(
            '''
            SELECT 
            availability_request.avail_request_id
            FROM availability_request 
            WHERE availability_request.avail_request_id 
            IN(
                SELECT avail_request_id FROM member_request WHERE member_request.member_id = ?
            )
            ''',
            (member_id, )
        ).fetchall()

############################ PROB MAKE HELPER FUNCTION ##########################
        page_data = []
        for elem in avail_request_ids:
            avail_request_id = elem[0]
            print("avail_request: ", avail_request_id)

            avail_request_name = db.execute(
                '''
                SELECT availability_request.avail_request_name
                FROM availability_request
                WHERE availability_request.avail_request_id = ?
                ''',
                (avail_request_id,)
            ).fetchone()[0]

            print("avail_request_name: ", avail_request_name)

            org_name = db.execute(
                '''
                SELECT organization.org_name 
                FROM organization 
                WHERE organization.org_id
                IN(
                    SELECT organization.org_id FROM availability_request WHERE availability_request.avail_request_id = ?
                )
                ''',
                (avail_request_id,)
            ).fetchone()[0]
            print("org_name: ", org_name)

            answered = db.execute(
                '''
                SELECT member_request.answered 
                FROM member_request 
                WHERE member_request.avail_request_id = ?
                AND member_request.member_id = ?
                ''',
                (avail_request_id, session['member_id'])
            ).fetchone()[0]
            print("answered: ",  answered)

            request_data = (avail_request_id, avail_request_name, org_name, answered)
            page_data.append(request_data)

    return render_template('member/index.html', orgs=orgs, avail_requests=page_data)

