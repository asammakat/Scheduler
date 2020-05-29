from flask import (
    Blueprint, flash, g, redirect, render_template, session, request, url_for
)
from werkzeug.exceptions import abort

from schedulerApp.auth import login_required
from schedulerApp.db import get_db

bp = Blueprint('organization', __name__)

@bp.route('/<int:org_id>/org_page', methods=('GET', 'POST'))
@login_required
def org_page(org_id):
    print("Hi from org page")
    #TODO: make it so that you cannot see orgs that you do not belong to(currently can type org id into the browser)
    db = get_db()
    org = db.execute(
        'SELECT * FROM organization WHERE org_id = ?',
        (org_id,)
    ).fetchone()
    print('before return')
    return render_template('organization/org_page.html', org=org)