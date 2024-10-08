import csv, regex
from datetime import datetime

from expense import app, db
from expense.models import Current, Future, History
from expense.utils import to_fractional, list_currencies


STRPTIME_FORMAT = app.config.get('DATE_FORMAT', '%Y-%m-%d')
DATE_FORMAT = '{:' + STRPTIME_FORMAT + '}'
CSV_COLUMNS = ['blank', 'name', 'value', 'created', 'settled', 'note']
LOCAL_CURRENCY = app.config.get('LOCAL_CURRENCY', 'USD')
PAGE_SIZE = app.config.get('PAGE_SIZE', 100)


def current_table(user):
    return [
        [
            e.id,
            e.name,
            e.formatted_local,
            e.formatted_value,
            DATE_FORMAT.format(e.created),
            e.note
        ]
        for e in user.current
    ]


def future_table(user):
    return [
        [
            e.id,
            e.name,
            e.formatted_local,
            e.formatted_value,
            DATE_FORMAT.format(e.due_date) if e.due_date else '',
            e.recur_summary,
            e.note
        ]
        for e in user.future
    ]


def historical_table(user, page=1):
    return [
        [
            e.id,
            e.name,
            e.formatted_local,
            e.formatted_value,
            DATE_FORMAT.format(e.created),
            DATE_FORMAT.format(e.settled),
            e.note
        ]
        for e in user.history.limit(PAGE_SIZE).offset((page - 1) * PAGE_SIZE)
    ]


def advance_current(user, current_id):
    expense = Current.query.get(current_id)
    if expense in user.current:
        expense.advance()
    else:
        raise Exception('User is not authorized to perform this action.')


def advance_future(user, future_id):
    expense = Future.query.get(future_id)
    if expense in user.future:
        expense.advance()
    else:
        raise Exception('User is not authorized to perform this action.')


def history_to_current(user, history_id):
    expense = History.query.get(history_id)
    if expense in user.history:
        expense.back()
    else:
        raise Exception('User is not authorized to perform this action.')


def add_current(user, fields):
    if 'id' in fields:
        edit_current(user, fields.pop('id'), fields)
    else:
        convert_fields(fields)
        expense = Current(**fields)
        user.current.append(expense)
        db.session.commit()


def add_future(user, fields):
    if 'id' in fields:
        edit_future(user, fields.pop('id'), fields)
    else:
        convert_fields(fields)
        expense = Future(**fields)
        user.future.append(expense)
        db.session.commit()


def add_history(user, fields):
    if 'id' in fields:
        edit_history(user, fields.pop('id'), fields)
    else:
        convert_fields(fields)
        expense = History(**fields)
        user.history.append(expense)
        db.session.commit()


def edit_current(user, current_id, fields):
    expense = Current.query.get(current_id)
    if expense in user.current:
        convert_fields(fields)
        for field, value in fields.items():
            setattr(expense, field, value)
        db.session.commit()
    else:
        raise Exception('User is not authorized to perform this action.')


def edit_future(user, future_id, fields):
    expense = Future.query.get(future_id)
    if expense in user.future:
        convert_fields(fields)

        # When due_date is changed on a recurring item, recur_base needs to be
        # reset (otherwise, it will recur based on the old date)
        if ("due_date" in fields) and ("recur_base" not in fields):
            fields["recur_base"] = None

        # Ensure that if recur_type is not sent, it's removed from the object
        if ("recur_type" not in fields):
            fields["recur_type"] = None

        for field, value in fields.items():
            setattr(expense, field, value)

        db.session.commit()
    else:
        raise Exception('User is not authorized to perform this action.')


def edit_history(user, history_id, fields):
    expense = History.query.get(history_id)
    if expense in user.history:
        convert_fields(fields)
        for field, value in fields.items():
            setattr(expense, field, value)
        db.session.commit()
    else:
        raise Exception('User is not authorized to perform this action.')


def delete_current(user, current_id):
    expense = Current.query.get(current_id)
    if expense in user.current:
        db.session.delete(expense)
        db.session.commit()
    else:
        raise Exception('User is not authorized to perform this action.')


def delete_future(user, future_id):
    expense = Future.query.get(future_id)
    if expense in user.future:
        db.session.delete(expense)
        db.session.commit()
    else:
        raise Exception('User is not authorized to perform this action.')


def delete_history(user, history_id):
    expense = History.query.get(history_id)
    if expense in user.history:
        db.session.delete(expense)
        db.session.commit()
    else:
        raise Exception('User is not authorized to perform this action.')


def convert_fields(fields):
    if 'value' in fields:
        if isinstance(fields['value'], str):
            # Remove thousands separators.
            value = fields['value'].replace(",", "")

            # Parse out sign, optional symbol, value, and optional currency.
            m = regex.search(
                r'(\p{Sc})?([-−(])?(\p{Sc})?([\d\.]+) ?(\w*)', value
            )

            sign = 1.0 if not m.group(2) else -1.0
            value = sign * float(m.group(4))

            currency = m.group(5).upper()
            if currency == 'US':
                currency = 'USD'

            if currency:
                if 'currency' in fields and \
                        fields['currency'] != currency.lower():
                    print(
                        f'Replacing currency {fields["currency"]} with '
                        f'{currency} parsed from {fields["value"]}.'
                    )
                elif currency.lower() not in list_currencies():
                    print(
                        f'Unable to validate currency {currency}. Assuming '
                        'local currency.'
                    )
                else:
                    fields['currency'] = currency

            if not currency:
                # Assuming value is a string (it's from the form), make sure
                # that it gets set to something (if it was previously set to a
                # foreign currency, it shouldn't necessarily remain set when
                # edited). This isn't an else because of the elif above.
                fields['currency'] = LOCAL_CURRENCY

            fields['value'] = value

        fields['value'] = to_fractional(fields['value'])
    else:
        fields['value'] = None

    for field in ['due_date', 'created', 'settled']:
        if field in fields:
            fields[field] = datetime.strptime(
                fields[field], STRPTIME_FORMAT
            ).date()

    if 'note' in fields:
        fields['note'] = fields['note'].strip()
    else:
        fields['note'] = ''


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


def save_csv(filename):
    # TODO
    pass
