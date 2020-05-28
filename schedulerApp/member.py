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
    # posts = db.execute(
    #     'SELECT p.id, title, body, created, author_id, username'
    #     ' FROM post p JOIN user u ON p.author_id = u.id'
    #     ' ORDER BY created DESC'
    # ).fetchall()
    member_id = session.get('member_id')
    if member_id is not None:
        orgs = db.execute(
            'SELECT organization.org_name FROM organization WHERE organization.org_id IN (SELECT roster.org_id FROM roster WHERE member_id = ?)', 
            (member_id,)
        ).fetchall()
        print(orgs)
    return render_template('member/index.html', orgs=orgs)

