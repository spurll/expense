from dateparser import parse

from expense import db
from expense.models import Current, Future, History
from expense.utils import to_fractional


DATE_FORMAT = '{:%Y-%m-%d}'


def current_table(user):
    # TODO: Might want an asterisk or something to indicate approximate values?
    return [
        [
            c.id,
            c.name,
            c.formatted_local,
            c.formatted_value,
            DATE_FORMAT.format(c.created),
            c.note
        ]
        for c in user.current
    ]


def future_table(user):
    return [
        [
            f.id,
            f.name,
            f.formatted_local,
            f.formatted_value,
            DATE_FORMAT.format(f.due_date),
            f.recur_summary,
            f.note
        ]
        for f in user.future
    ]


def historical_table(user):
    return [
        [
            h.id,
            h.name,
            h.formatted_local,
            h.formatted_value,
            DATE_FORMAT.format(h.created),
            DATE_FORMAT.format(h.settled),
            h.note
        ]
        for h in user.history
    ]


def add_current(user, fields):
    convert_fields(fields)
    expense = Current(**fields)
    user.current.append(expense)
    db.session.commit()


def add_future(user, fields):
    convert_fields(fields)
    expense = Future(**fields)
    user.future.append(expense)
    db.session.commit()


def add_history(user, fields):
    convert_fields(fields)
    expense = History(**fields)
    user.history.append(expense)
    db.session.commit()


def edit_current(current_id, fields):
    expense = Current.query.get(current_id)
    convert_fields(fields)
    for field, value in fields.items():
        setattr(expense, field, value)
    db.session.commit()


def edit_future(future_id, fields):
    expense = Future.query.get(future_id)
    convert_fields(fields)
    for field, value in fields.items():
        setattr(expense, field, value)
    db.session.commit()


def edit_history(history_id, fields):
    expense = History.query.get(history_id)
    convert_fields(fields)
    for field, value in fields.items():
        setattr(expense, field, value)
    db.session.commit()


def delete_current(current_id):
    expense = Current.query.get(current_id)
    db.session.delete(expense)
    db.session.commit()


def delete_future(future_id):
    expense = Future.query.get(future_id)
    db.session.delete(expense)
    db.session.commit()


def delete_history(history_id):
    expense = History.query.get(history_id)
    db.session.delete(expense)
    db.session.commit()


def convert_fields(fields):
    if 'value' in fields:
        fields['value'] = to_fractional(fields['value'])

    if 'due_date' in fields:
        fields['due_date'] = parse(fields['due_date']).date()

    if 'created' in fields:
        fields['created'] = parse(fields['current']).date()


def load_from_csv(filename, historical=False):
    # TODO: Grab this from the cards thing.
    # Does it replace the whole thing? Or just insert?
    pass


def save_to_csv(filename, historical=False):
    # TODO: Grab this from the cards thing.
    pass
