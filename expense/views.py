from flask import render_template, flash, redirect, session, url_for, request
from flask.ext.login import login_user, logout_user, current_user, login_required
import ldap3

from expense import app, db, lm
from expense.forms import LoginForm, CurrentForm
from expense.models import User
from expense.authenticate import authenticate
from expense.controller import current_table, future_table, historical_table
from expense.utils import list_currencies


@app.route('/')
@app.route('/index')
@login_required
def main():
    """
    View/edit current/future expenses.
    """
#    form = CurrentForm()

#    if not objects:
#        flash("You don't have any objects.")

    total = current_user.formatted_total
    current = current_table(current_user)
    future = future_table(current_user)

    # List of currencies:
    # list_currencies()



#   TODO: Throw away basically all of this stuff and do everything in AJAX




    return render_template(
        'main.html', title='Expense', user=current_user, total=total,
        current=current, future=future,
        link={'url': url_for('history'), 'text': 'History'}
    )

#    return redirect(url_for("main"))


@app.route('/history')
@login_required
def history():
    """
    View expense history.
    """
    pass


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Logs the user in using LDAP authentication.
    """
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))

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

            return redirect(request.args.get('next') or url_for('index'))

    return render_template('login.html', title="Log In", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@lm.user_loader
def load_user(id):
    return User.query.get(id)
