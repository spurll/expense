from datetime import date, timedelta

from expense import app, db
from expense.controller import complex_recur, increment_month, safe_date, convert_currency


class User(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, index=True, unique=True)
    email = db.Column(db.String, index=True)
    current = db.relationship(
        'Current', backref='user', order_by='Current.created', lazy='dynamic',
        cascade='all, delete-orphan'
    )
    future = db.relationship(
        'Future', backref='user', order_by='Future.due_date', lazy='dynamic',
        cascade='all, delete-orphan'
    )
    history = db.relationship(
        'History', backref='user', order_by='History.created', lazy='dynamic',
        cascade='all, delete-orphan'
    )

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def is_admin(self):
        return self.id in app.config["ADMIN_USERS"]

    def get_id(self):
        return self.id

    def current_total(self):
        return 

    def __repr__(self):
        return '<User {}>'.format(self.id)


# TODO: Seems like these should inherit from a common class to avoid repetition
# of fields and function declarations (e.g., local_value).

class Current(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    value = db.Column(db.Integer)
    currency = db.Column(db.String(3), default='CAD')
    note = db.Column(db.String)
    created = db.Column(db.Date, default=date.today)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @property
    def local_value(self):
        """
        Returns the value of the expense in the local currency.
        """
        local = app.config['LOCAL_CURRENCY']
        return convert_currency(self.value, self.currency, local, self.created)

    @property
    def formatted_value(self):
        """
        Returns the value of the expense, formatted for display.
        """
        return '{:.2f} {}'.format(self.local_value / 100.0, self.currency)

    @property
    def formatted_local(self):
        """
        Returns the local value of the expense, formatted for display.
        """
        return '{}{:.2f}'.format(
            app.config['LOCAL_SYMBOL'], self.local_value / 100.0
        )

    def advance(self):
        """
        Copy row to History, then delete.
        """
        pass    # TODO

    def __repr__(self):
        return '<Current {}>'.format(self.id)

    def __str__(self):
        return '<Current Expense: {}, {}>'.format(self.name, self.value)


class Future(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    value = db.Column(db.Integer)
    currency = db.Column(db.String(3), default='CAD')
    note = db.Column(db.String)
    due_date = db.Column(db.Date)
    recur_base = db.Column(db.Date)
    recur_type = db.Column(db.String(1))    # Y, M, W, D, R
    recur_freq = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Special recur_type R has no recur_freq or recur_base (it just keeps the
    # item from disappearing from the recurring list for quick access).

    @property
    def local_value(self):
        """
        Returns the value of the expense in the local currency.
        """
        local = app.config['LOCAL_CURRENCY']
        return convert_currency(self.value, self.currency, local, date.today())

    @property
    def formatted_value(self):
        """
        Returns the value of the expense, formatted for display.
        """
        return '{:.2f} {}'.format(self.local_value / 100.0, self.currency)

    @property
    def formatted_local(self):
        """
        Returns the local value of the expense, formatted for display.
        """
        return '{}{:.2f}'.format(
            app.config['LOCAL_SYMBOL'], self.local_value / 100.0
        )

    @property
    def recur(self):
        return self.recur_type is not None

    @property
    def recur_summary(self):
        if not self.recur:
            return ''
        elif not self.recur_freq:
            return self.recur_type
        else:
            return '{}{}'.format(self.recur_freq, self.recur_base)

    def advance(self):
        """
        Copy row to Current. If recur, set due_date to next, otherwise delete.
        """
        pass    # TODO

    def update_due_date(self):
        """
        Updates the due_date for recurring items. The base_date is only
        important when incrementing by months or years, where we don't want to
        screw up day information (e.g., recur every month on the 30th).
        """
        if self.recur_type == 'D':
            self.due_date += timedelta(days=self.recur_freq)

        elif self.recur_type == 'W':
            self.due_date += timedelta(weeks=self.recur_freq)

        elif self.recur_type == 'M':
            op = lambda d, i: increment_month(d, self.recur_freq * i)
            self.due_date = complex_recur(
                self.recur_base, op, lambda dt: dt > self.due_date
            )

        elif self.recur_type == 'Y':
            op = lambda d, i: safe_date(
                d.year + self.recur_freq * i, d.month, d.day
            )
            self.due_date = complex_recur(
                self.recur_base, op, lambda dt: dt > self.due_date
            )

    def __repr__(self):
        return '<Future {}>'.format(self.id)

    def __str__(self):
        return '<Future Expense: {}, {}{}>'.format(
            self.name, self.value,
            ' (Recurring)' if self.recur_type is not None else ''
        )


    # TODO: Should commits happen here? (advance, update_due_date, etc.) or in
    # the controller?


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    value = db.Column(db.Integer)
    currency = db.Column(db.String(3), default='CAD')
    note = db.Column(db.String)
    created = db.Column(db.Date)
    settled = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @property
    def local_value(self):
        """
        Returns the value of the expense in the local currency.
        """
        local = app.config['LOCAL_CURRENCY']
        return convert_currency(self.value, self.currency, local, self.created)

    @property
    def formatted_value(self):
        """
        Returns the value of the expense, formatted for display.
        """
        return '{:.2f} {}'.format(self.local_value / 100.0, self.currency)

    @property
    def formatted_local(self):
        """
        Returns the local value of the expense, formatted for display.
        """
        return '{}{:.2f}'.format(
            app.config['LOCAL_SYMBOL'], self.local_value / 100.0
        )

    def __repr__(self):
        return '<Historical {}>'.format(self.id)

    def __str__(self):
        return '<Historical Expense: {}, {}, {}>'.format(
            self.date, self.name, self.value
        )
