from flask import render_template, flash, jsonify, redirect, session, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from functools import partial
import ldap3

from expense import app, db, lm
from expense.forms import *
from expense.models import User
from expense.authenticate import authenticate
from expense.controller import *
from expense.utils import list_currencies, error, get_errors


@app.route('/')
@login_required
def main():
    """
    View/edit current/future expenses.
    """
    return render_template(
        'main.html', title='Expenses', user=current_user,
        use_loading_gif=app.config.get('LOADING_GIF'),
        confirm_deletion=app.config.get('CONFIRM_DELETION'),
        current_form=CurrentForm(), future_form=FutureForm(),
        edit_current_form=EditCurrentForm(), edit_future_form=EditFutureForm(),
        link={'url': url_for('history'), 'text': 'History'}
    )


@app.route('/history')
@login_required
def history():
    """
    View expense history.
    """
    return render_template(
        'history.html', title='Expenses', user=current_user,
        edit_history_form=EditHistoryForm(),
        use_loading_gif=app.config.get('LOADING_GIF'),
        confirm_deletion=app.config.get('CONFIRM_DELETION'),
        link={'url': url_for('main'), 'text': 'Back'}
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Logs the user in using LDAP authentication.
    """
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('main'))

    form = LoginForm()

    if request.method == 'GET':
        return render_template('login.html', title="Log In", form=form)

    if form.validate_on_submit():
        user, message = authenticate(form.username.data, form.password.data)

        if not user:
            flash(f'Login failed: {message}.')
            return render_template('login.html', title='Log In', form=form)

        if user and user.is_authenticated:
            db_user = User.query.get(user.id)
            if db_user is None:
                db.session.add(user)
                db.session.commit()

            login_user(user, remember=form.remember.data)

            return redirect(request.args.get('next') or url_for('main'))

    return render_template('login.html', title="Log In", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main'))


@lm.user_loader
def load_user(id):
    return User.query.get(id)


# AJAX BACK-END
# Don't use @login_required, because that will trigger a login redirect.

@app.route('/_load_table')
def load_table():
    """
    Return all current expenses.
    """
    if current_user is None or not current_user.is_authenticated:
        return jsonify(data={}, errors=['User log in.'], reload=True)

    data = {}
    fn = None

    table = request.args.get('table', None)

    if table == 'current':
        fn = current_table
    elif table == 'future':
        fn = future_table
    elif table == 'history':
        fn = partial(historical_table, page=int(request.args.get('page', '1')))

    if fn:
        try:
            data[table] = fn(current_user)
            data['total'] = table == 'current' and current_user.formatted_total
        except Exception as e:
            error(e)
    else:
        error(f'Attempted to load invalid table {table}.')

    return jsonify(data=data, errors=get_errors())


@app.route('/_total')
def total():
    """
    Return the total value (in local currency) of all current expenses.
    """
    if current_user is None or not current_user.is_authenticated:
        return jsonify(data={}, errors=['User log in.'], reload=True)

    data = None

    try:
        data = current_user.formatted_total
    except Exception as e:
        error(str(e))

    return jsonify(data=data, errors=get_errors())


@app.route('/_add_expense', methods=['POST'])
def add_expense():
    """
    Adds or edits an expense.
    """
    if current_user is None or not current_user.is_authenticated:
        return jsonify(data={}, errors=['User log in.'], reload=True)

    fn = None

    # Make it mutable.
    args = {k: v for (k, v) in request.form.items() if v is not ''}
    table = args.pop('table', None)

    if not args.get('name'):
        return jsonify(data={}, errors=['Item name is required.'])

    if table == 'current':
        fn = add_current
    elif table == 'future':
        fn = add_future
    elif table == 'history':
        fn = add_history
    else:
        error(f'Attempted to edit an invalid table {table}.')

    try:
        print(f'Adding {table} expense: {args}')
        fn(current_user, args)
    except Exception as e:
        error(str(e))

    return jsonify(errors=get_errors())


@app.route('/_settle', methods=['POST'])
def settle():
    """
    Move an expense from Current to History.
    """
    if current_user is None or not current_user.is_authenticated:
        return jsonify(data={}, errors=['User log in.'], reload=True)

    try:
        print(f'Settling current expense: {request.form.get("id")}')
        advance_current(current_user, request.form.get('id', None, type=int))
    except Exception as e:
        error(str(e))

    return jsonify(errors=get_errors())


@app.route('/_advance', methods=['POST'])
def advance():
    """
    Move an expense from Future to Current.
    """
    if current_user is None or not current_user.is_authenticated:
        return jsonify(data={}, errors=['User log in.'], reload=True)

    try:
        print(f'Advancing future expense: {request.form.get("id")}')
        advance_future(current_user, request.form.get('id', None, type=int))
    except Exception as e:
        error(str(e))

    return jsonify(errors=get_errors())


@app.route('/_send_back', methods=['POST'])
def send_back():
    """
    Move an expense from History back to Current.
    """
    if current_user is None or not current_user.is_authenticated:
        return jsonify(data={}, errors=['User log in.'], reload=True)

    try:
        print(f'Sending expense back to current: {request.form}')
        history_to_current(current_user,request.form.get('id', None, type=int))
    except Exception as e:
        error(str(e))

    return jsonify(errors=get_errors())


@app.route('/_delete', methods=['POST'])
def delete():
    """
    Delete an expense.
    """
    if current_user is None or not current_user.is_authenticated:
        return jsonify(data={}, errors=['User log in.'], reload=True)

    table = request.form.get('table', None)

    if table == 'current':
        fn = delete_current
    elif table == 'future':
        fn = delete_future
    elif table == 'history':
        fn = delete_history

    try:
        print(f'Deleting {table} expense: {request.form.get("id")}')
        fn(current_user, request.form.get('id', None, type=int))
    except Exception as e:
        error(str(e))

    return jsonify(errors=get_errors())
