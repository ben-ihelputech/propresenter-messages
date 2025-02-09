from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from kids_messages.auth import login_required
from kids_messages.db import get_db

import re 

bp = Blueprint('messages', __name__)

@bp.route('/')
def index():
    db = get_db()
    messages = db.execute(
        'SELECT p.id, message, created, author_id, username'
        ' FROM message_logs p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('messages/index.html', messages=messages)

@bp.route('/new-message', methods=('GET', 'POST'))
@login_required
def new_message():
    if request.method == 'POST':
        message = request.form['message']
        error = None

        if not message:
            error = 'Message Code is required.'

        # Convert all case to upper
        # message = message.capitalize[str]

        # Message validation
        # filter = '[A-Z][0-9][A-Z]'
        # def validate_text(text, pattern):
        #     return bool(re.match(pattern, text))
        # if validate_text(message, filter) is not True:
        #     error = 'Invalid Message Code'


        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO message_logs (message, author_id)'
                ' VALUES (?, ?)',
                (message, g.user['id'])
            )
            db.commit()
            return redirect(url_for('messages.index'))

    return render_template('messages/new-message.html')

def get_message(id, check_author=True):
    message = get_db().execute(
        'SELECT p.id, message, created, author_id, username'
        ' FROM message_logs p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if message is None:
        abort(404, f"Message id {id} doesn't exist.")

    if check_author and message['author_id'] != g.user['id']:
        abort(403)

    return message

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    message = get_message(id)

    if request.method == 'POST':
        message = request.form['message']
        error = None

        if not message:
            error = 'Message is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE message_logs SET messsage = ?'
                ' WHERE id = ?',
                (message, id)
            )
            db.commit()
            return redirect(url_for('messages.index'))

    return render_template('messages/update.html', post=message)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_message(id)
    db = get_db()
    db.execute('DELETE FROM message_logs WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('messages.index'))