from flask import render_template, jsonify, redirect, session, url_for, request
from flask.ext.login import login_user, logout_user, current_user, login_required
import ldap3

from expense import app, db, lm
from expense.forms import LoginForm, CurrentForm, FutureForm
from expense.models import User
from expense.authenticate import authenticate
from expense.controller import *
from expense.utils import list_currencies


@app.route('/')
@login_required
def main():
    """
    View/edit current/future expenses.
    """
    return render_template(
        'main.html', title='Expenses', user=current_user,
        use_loading_gif=app.config.get('LOADING_GIF'),
        current_form=CurrentForm(), future_form=FutureForm(),
        link={'url': url_for('history'), 'text': 'History'}
    )


@app.route('/history')
@login_required
def history():
    """
    View expense history.
    """
    return render_template(
        'history.html', title='Expense History', user=current_user,
        use_loading_gif=app.config.get('LOADING_GIF'),
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
        user = authenticate(form.username.data, form.password.data)

        if not user:
            flash('Login failed.')
            return render_template('login.html', title="Log In", form=form)

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


@app.route('/_load_table')
@login_required
def load_table():
    """
    Return all current expenses.
    """
    data = {}
    error = None
    fn = None

    table = request.args.get('table', None)

    if table == 'current':
        fn = current_table
    elif table == 'future':
        fn = future_table
    elif table == 'history':
        fn = historical_table

    if fn:
        try:
            data[table] = fn(current_user)
            data['total'] = table == 'current' and current_user.formatted_total
        except Exception as e:
            print(e)
            error = str(e)
    else:
        error = 'Attempted to load invalid table {}.'.format(table)

    return jsonify(data=data, error=error)


@app.route('/_add_expense')
@login_required
def add_expense():
    """
    Adds a current expense.
    """
    fn = None
    error = None

    # Make it mutable.
    args = {k: v for (k, v) in request.args.items() if v is not None}
    table = args.pop('table', None)

    if table == 'current':
        fn = add_current
    elif table == 'future':
        fn = add_future
    elif table == 'history':
        fn = add_history

    if fn:
        try:
            fn(current_user, args)
        except Exception as e:
            print(e)
            error = str(e)
    else:
        error = 'Attempted to edit an invalid table {}.'.format(table)

    return jsonify(error=error)


@app.route('/_total')
@login_required
def total():
    """
    Return the total value (in local currency) of all current expenses.
    """
    data = None
    error = None

    try:
        data = current_user.formatted_total
    except Exception as e:
        print(e)
        error = str(e)

    return jsonify(data=data, error=error)


@app.route('/_settle')
@login_required
def settle():
    """
    Move an expense from Current to History.
    """
    error = None

    try:
        advance_current(current_user, request.args.get('id', None, type=int))
    except Exception as e:
        print(e)
        error = str(e)

    return jsonify(error=error)


@app.route('/_advance')
@login_required
def advance():
    """
    Move an expense from Future to Current.
    """
    error = None

    try:
        advance_future(current_user, request.args.get('id', None, type=int))
    except Exception as e:
        print(e)
        error = str(e)

    return jsonify(error=error)


@app.route('/_send_back')
@login_required
def send_back():
    """
    Move an expense from History back to Current.
    """
    error = None

    try:
        history_to_current(current_user,request.args.get('id', None, type=int))
    except Exception as e:
        print(e)
        error = str(e)

    return jsonify(error=error)


@app.route('/_delete')
@login_required
def delete():
    """
    Delete an expense.
    """
    error = None

    table = request.args.get('table', None)

    if table == 'current':
        fn = delete_current
    elif table == 'future':
        fn = delete_future
    elif table == 'history':
        fn = delete_history

    try:
        fn(current_user, request.args.get('id', None, type=int))
    except Exception as e:
        print(e)
        error = str(e)

    return jsonify(error=error)
