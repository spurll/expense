from flask.ext.wtf import Form
from wtforms import TextField, HiddenField, PasswordField, BooleanField, SelectField, DateField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import Required


class LoginForm(Form):
    username = TextField("Username", validators=[Required()])
    password = PasswordField("Password", validators=[Required()])
    remember = BooleanField("Remember Me", default=False)


class CurrentForm(Form):
    id = HiddenField('ID')
    name = TextField('Name')
    value = TextField('Value')
    created = DateField('Created')
    currency = SelectField('Currency')
    note = TextField('Note')


class FutureForm(Form):
    id = HiddenField('ID')
    name = TextField('Name')
    value = TextField('Value')
    due_date = DateField('Due Date')
    recur_freq = IntegerField('Recur Frequency')
    recur_type = SelectField(
        'Recur Type', choices=[
            ('', ''),
            ('R', 'R'),
            ('D', 'D'),
            ('W', 'W'),
            ('M', 'M'),
            ('Y', 'Y')
        ]
    )
    note = TextField('Note')

class HistoryForm(Form):
    pass    # TODO?
