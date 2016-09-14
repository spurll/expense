from flask import render_template,flash,redirect,session,url_for,request,g
from flask.ext.login import login_user,logout_user,current_user,login_required
import ldap3

from expense import app, db, lm
from expense.forms import LoginForm, CurrentForm
from expense.models import User
from expense.authenticate import authenticate
from expense.controller import current_table, future_table, historical_table


@app.route('/')
@app.route('/index')
@login_required
def main():
    """
    Views objects.
    """
    user = g.user
    objects = user.objects

    form = CurrentForm()

    if not objects:
        flash("You don't have any objects.")

    # TODO: Include a total
    total = user.current_total
    current = current_table(user)
    future = future_table(user)

    return render_template(
        "view.html", title="View", user=user, links=None, form=form,
        objects=objects
    )

#    return redirect(url_for("main"))


@app.route('/history')
@login_required
def history():
    """
    Views history.
    """
    user = g.user


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Logs the user in using LDAP authentication.
    """
    if g.user is not None and g.user.is_authenticated:
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
