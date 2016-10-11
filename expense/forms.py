from flask.ext.wtf import Form
from wtforms import TextField, HiddenField, PasswordField, BooleanField, SelectField, DateField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import Required


class LoginForm(Form):
    username = TextField("Username", validators=[Required()])
    password = PasswordField("Password", validators=[Required()])
    remember = BooleanField("Remember Me", default=False)


class CurrentForm(Form):
    name = TextField('Name', id="current_name")
    value = TextField('Value', id="current_value")
    created = DateField('Created', id="current_created")
    note = TextField('Note', id="current_note")


class EditCurrentForm(Form):
    id = HiddenField('ID', id="edit_current_id")
    name = TextField('Name', id="edit_current_name")
    value = TextField('Value', id="edit_current_value")
    created = DateField('Created', id="edit_current_created")
    note = TextField('Note', id="edit_current_note")


class FutureForm(Form):
    id = HiddenField('ID', id="future_id")
    name = TextField('Name', id="future_name")
    value = TextField('Value', id="future_value")
    due_date = DateField('Due Date', id="future_due_date")
    recur_freq = IntegerField('Recur Frequency', id="future_recur_freq")
    recur_type = SelectField(
        'Recur Type', id="future_recur_type", choices=[
            ('', ''),
            ('R', 'R'),
            ('D', 'D'),
            ('W', 'W'),
            ('M', 'M'),
            ('Y', 'Y')
        ]
    )
    note = TextField('Note', id="future_note")


class EditFutureForm(Form):
    id = HiddenField('ID', id="edit_future_id")
    name = TextField('Name', id="edit_future_name")
    value = TextField('Value', id="edit_future_value")
    due_date = DateField('Due Date', id="edit_future_due_date")
    recur_freq = IntegerField('Recur Frequency', id="edit_future_recur_freq")
    recur_type = SelectField(
        'Recur Type', id="edit_future_recur_type", choices=[
            ('', ''),
            ('R', 'R'),
            ('D', 'D'),
            ('W', 'W'),
            ('M', 'M'),
            ('Y', 'Y')
        ]
    )
    note = TextField('Note', id="edit_future_note")


class EditHistoryForm(Form):
    id = HiddenField('ID', id="edit_history_id")
    name = TextField('Name', id="edit_history_name")
    value = TextField('Value', id="edit_history_value")
    created = DateField('Created', id="edit_history_created")
    settled = DateField('Settled', id="edit_history_settled")
    note = TextField('Note', id="edit_history_note")
