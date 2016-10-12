from datetime import date, timedelta

from expense import app, db
from expense.utils import complex_recur, increment_month, safe_date, convert_currency, to_major


LOCAL_CURRENCY = app.config.get('LOCAL_CURRENCY', 'USD')


class User(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, index=True, unique=True)
    email = db.Column(db.String, index=True)
    current = db.relationship(
        'Current', backref='user', order_by='Current.created.desc()',
        lazy='dynamic', cascade='all, delete-orphan'
    )
    future = db.relationship(
        'Future', backref='user', order_by='Future.due_date.asc()',
        lazy='dynamic', cascade='all, delete-orphan'
    )
    history = db.relationship(
        'History', backref='user', order_by='History.created.desc()',
        lazy='dynamic', cascade='all, delete-orphan'
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

    @property
    def current_total(self):
        return sum(c.local_value for c in self.current if c.local_value)

    @property
    def formatted_total(self):
        return '{}{:,.2f}'.format(
            app.config['LOCAL_SYMBOL'], to_major(self.current_total)
        )

    def __repr__(self):
        return '<User {}>'.format(self.id)


# TODO: Seems like these should inherit from a common class to avoid repetition
# of fields and function declarations (e.g., local_value).

class Current(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, nullable=False)
    value = db.Column(db.Integer)
    currency = db.Column(db.String(3), default=LOCAL_CURRENCY, nullable=False)
    note = db.Column(db.String, default='', nullable=False)
    created = db.Column(db.Date, default=date.today)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @property
    def local_value(self):
        """
        Returns the value of the expense in the local currency.
        """
        return convert_currency(
            self.value, self.currency, LOCAL_CURRENCY, self.created
        ) if self.value is not None else None

    @property
    def formatted_value(self):
        """
        Returns the value of the expense, formatted for display.
        """
        return '{:,.2f} {}'.format(to_major(self.value), self.currency) \
            if self.value is not None else '—'

    @property
    def formatted_local(self):
        """
        Returns the local value of the expense, formatted for display.
        """
        return '{}{:,.2f}'.format(
            app.config['LOCAL_SYMBOL'], to_major(self.local_value)
        ) if self.local_value is not None else '—'

    def advance(self):
        """
        Copy row to History, then delete. Commit changes to DB session.
        """
        expense = History(
            name=self.name,
            value=self.value,
            currency=self.currency,
            note=self.note,
            created=self.created
        )
        self.user.history.append(expense)
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Current {}>'.format(self.id)

    def __str__(self):
        return '<Current Expense: {}, {}>'.format(self.name, self.value)


class Future(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, nullable=False)
    value = db.Column(db.Integer)
    currency = db.Column(db.String(3), default=LOCAL_CURRENCY, nullable=False)
    note = db.Column(db.String, default='', nullable=False)
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
        return convert_currency(
            self.value, self.currency, LOCAL_CURRENCY, date.today()
        ) if self.value is not None else None

    @property
    def formatted_value(self):
        """
        Returns the value of the expense, formatted for display.
        """
        return '{:,.2f} {}'.format(to_major(self.value), self.currency) \
            if self.value is not None else '—'

    @property
    def formatted_local(self):
        """
        Returns the local value of the expense, formatted for display.
        """
        return '{}{:,.2f}'.format(
            app.config['LOCAL_SYMBOL'], to_major(self.local_value)
        ) if self.local_value is not None else '—'

    @property
    def recur(self):
        return self.recur_type is not None

    @property
    def recur_summary(self):
        if not self.recur:
            return ''
        elif not self.recur_freq or self.recur_freq == 1:
            return self.recur_type
        else:
            return '{}{}'.format(self.recur_freq, self.recur_type)

    def advance(self):
        """
        Copy row to Current. If recur, set due_date to next, otherwise delete.
        Then commit changes to DB session.
        """
        expense = Current(
            name=self.name,
            value=self.value,
            currency=self.currency,
            note=self.note,
            created=date.today()
        )
        self.user.current.append(expense)

        if self.recur:
            self.update_due_date()
        else:
            db.session.delete(self)

        db.session.commit()

    def update_due_date(self):
        """
        Updates the due_date for recurring items. The base_date is only
        important when incrementing by months or years, where we don't want to
        screw up day information (e.g., recur every month on the 30th).
        """
        # In case recur_freq, due_date, or base_date weren't set...
        recur_freq = self.recur_freq or 1
        due_date = self.due_date or date.today()
        self.recur_base = self.recur_base or due_date
        # If recur_base isn't set, save it to the object.

        if self.recur_type == 'D':
            self.due_date = due_date + timedelta(days=recur_freq)

        elif self.recur_type == 'W':
            self.due_date = due_date + timedelta(weeks=recur_freq)

        elif self.recur_type == 'M':
            op = lambda d, i: increment_month(d, recur_freq * i)
            self.due_date = complex_recur(
                self.recur_base, op, lambda dt: dt > due_date
            )

        elif self.recur_type == 'Y':
            op = lambda d, i: safe_date(
                d.year + recur_freq * i, d.month, d.day
            )
            self.due_date = complex_recur(
                self.recur_base, op, lambda dt: dt > due_date
            )

    def __repr__(self):
        return '<Future {}>'.format(self.id)

    def __str__(self):
        return '<Future Expense: {}, {}{}>'.format(
            self.name, self.value,
            ' (Recurring)' if self.recur_type is not None else ''
        )


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, nullable=False)
    value = db.Column(db.Integer)
    currency = db.Column(db.String(3), default=LOCAL_CURRENCY, nullable=False)
    note = db.Column(db.String, default='', nullable=False)
    created = db.Column(db.Date, default=date.today)
    settled = db.Column(db.Date, default=date.today)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @property
    def local_value(self):
        """
        Returns the value of the expense in the local currency.
        """
        return convert_currency(
            self.value, self.currency, LOCAL_CURRENCY, self.created
        ) if self.value is not None else None

    @property
    def formatted_value(self):
        """
        Returns the value of the expense, formatted for display.
        """
        return '{:,.2f} {}'.format(to_major(self.value), self.currency) \
            if self.value is not None else '—'

    @property
    def formatted_local(self):
        """
        Returns the local value of the expense, formatted for display.
        """
        return '{}{:,.2f}'.format(
            app.config['LOCAL_SYMBOL'], to_major(self.local_value)
        ) if self.local_value is not None else '—'

    def back(self):
        """
        Copy row to Current, then delete. Commit changes to DB session.
        """
        expense = Current(
            name=self.name,
            value=self.value,
            currency=self.currency,
            note=self.note,
            created=self.created
        )
        self.user.current.append(expense)
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Historical {}>'.format(self.id)

    def __str__(self):
        return '<Historical Expense: {}, {}, {}>'.format(
            self.date, self.name, self.value
        )
