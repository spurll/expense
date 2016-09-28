import csv, re
from dateparser import parse

from expense import db
from expense.models import Current, Future, History
from expense.utils import to_fractional, list_currencies


DATE_FORMAT = '{:%Y-%m-%d}'
CSV_COLUMNS = ['blank', 'name', 'value', 'created', 'settled', 'note']


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
        if isinstance(fields['value'], str):
            # Parse out the string value (and potential currency).
            m = re.search(r'\$?([\d\.]+) ?(\w*)', fields['value'])
            value = float(m.group(1))
            currency = m.group(2) if m.group(2) != 'US' else 'USD'

            if currency:
                if 'currency' in fields and fields['currency'] != currency:
                    print(
                        'Replacing currency {} with {} parsed from {}.'.format(
                            fields['currency'], currency, fields['value']
                        )
                    )
                elif currency not in list_currencies():
                    print(
                        'Unable to validate currency {}. Assuming local '
                        'currency.'.format(currency)
                    )
                else:
                    fields['currency'] = currency

            fields['value'] = value

        fields['value'] = to_fractional(fields['value'])

    for field in ['due_date', 'created', 'settled']:
        if field in fields:
            fields[field] = parse(fields[field]).date()


def load_csv(user, filename, add_function=add_current):
    """
    Takes a file name and imports all rows into the table of expenses using
    the add_function supplied (defaults to add_current).
    """
    with open(filename, 'r') as csv_file:
        reader = csv.reader(csv_file)

        # Skip the header.
        next(reader, None)

        for r in reader:
            add_function(
                user,
                {c: r[i] for i, c in enumerate(CSV_COLUMNS) if r[i]}
                # Will skip values of 0, but that's fine, right?
            )


def save_current_csv(filename):
    # TODO
    pass
