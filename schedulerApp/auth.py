import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from schedulerApp.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.member is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT member_id FROM member WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO member (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)
    return render_template('auth/register.html')

@bp.route('/register_org', methods=('GET', 'POST'))
@login_required
def register_org():
    ''' Insert a new organization into the database. '''
    if request.method == 'POST':
        org_name = request.form['org_name']
        password = request.form['password']
        db = get_db()
        error = None

        if not org_name:
            error = 'Organization name is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT org_id FROM organization WHERE org_name = ?', (org_name,)
        ).fetchone() is not None:
            error = '{} is already registered.'.format(org_name)

        if error is None:
            db.execute(
                'INSERT INTO organization (org_name, password) VALUES (?, ?)',
                (org_name, generate_password_hash(password))
            )
            db.commit()

            #automatically add current user to roster
            org_id = db.execute(
                'SELECT org_id FROM organization WHERE org_name = ?', (org_name,)
            ).fetchone()[0]

            member_id = session['member_id']

            db.execute(
                'INSERT INTO roster (org_id, member_id) VALUES (?, ?)',
                (org_id, member_id,)
            )
            db.commit()
            flash("New Organization registered")

            return redirect(url_for('member.index'))

        flash(error)

    return render_template('auth/register_org.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        member = db.execute(
            'SELECT * FROM member WHERE username = ?', (username,)
        ).fetchone()

        member_password = None

        if member is None:
            error = 'Incorrect username.'
        else:
            member_password = member[2]

        if member_password is not None and not check_password_hash(member_password, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['member_id'] = member[0]
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/add_to_roster', methods=('GET', 'POST'))
@login_required
def add_to_roster():
    if request.method == 'POST':
        org_name = request.form['org_name']
        password = request.form['password']
        db = get_db()
        error = None
        organization = db.execute(
            'SELECT * FROM organization WHERE org_name = ?', (org_name,)
        ).fetchone()

        member_id = session['member_id']
        org_pword = None
        org_id = None

        if organization is None:
            error = 'This organization does not exist.'
        else:
            org_pword = organization[2]
            org_id = organization[0]

        if org_pword is not None and not check_password_hash(org_pword, password):
            error = 'Incorrect password.'
        elif db.execute(
            'SELECT * FROM roster WHERE org_id = ?',
            (org_id,)
        ).fetchone() is not None:
            error = 'You are already in the organization.'

        if error is None:
            db.execute(
                'INSERT INTO roster (org_id, member_id) VALUES (?, ?)',
                (org_id, member_id,)
            )
            db.commit()
            flash("join successful!")
            return redirect(url_for('index'))

        flash(error)    
    return render_template('auth/add_to_roster.html')

@bp.before_app_request
def load_logged_in_user():
    member_id = session.get('member_id')

    if member_id is None:
        g.member = None
    else:
        g.member = get_db().execute(
            'SELECT * FROM member WHERE member_id = ?', (member_id,)
        ).fetchone()
    
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
