from datetime import date
from calendar import monthrange
import requests


RATE_REQUEST = 'http://api.fixer.io/{date:%Y-%m-%d}?base={src}&symbols={dst}'

rate_cache = {}


def current_table(user):
    # TODO: Might want an asterisk or something to indicate approximate values?
    return [
        [c.name, c.formatted_local, c.formatted_value, c.created, c.note]
        for c in user.current
    ]


def future_table(user):
    return [
        [
            f.name,
            f.formatted_local,
            f.formatted_value,
            f.due_date,
            f.recur_summary,
            f.note
        ]
        for f in user.future
    ]


def historical_table(user):
    return [
        [
            h.name,
            h.formatted_local,
            h.formatted_value,
            h.created,
            h.settled,
            h.note
        ]
        for h in user.history
    ]


def convert_currency(value, src, dst, date):
    return value * (conversion_rate(date, src, dst) if src != dst else 1)


def conversion_rate(src, dst, date):
    """
    Returns the historical conversion rate between two currencies.
    """
    request = RATE_REQUEST.format(date=date, src=src, dst=dst)

    if request not in rate_cache:
        r = requests.get(request)

        if r.status_code == 200:
            rate = r.json().get('rates', {}).get(dst)

            if rate is not None:
                rate_cache[request] = rate
            else:
                print('No rate for {} found. Request returned: {}'.format(
                    dst, r.text
                ))
        else:
            print('No rate for {} found. Request returned a {}.'.format(
                dst, r.status_code
            ))

    return rate_cache.get(request)


def recur(x, operation, condition):
    """
    Performs operation on x until x satisfies condition.
    """
    while not condition(x):
        x = operation(x)
    return x


def complex_recur(x, operation, condition):
    """
    Performs operation on x until x satisfies condition; operation must accept
    both x and an increment. When recurring over increment_month, for example,
    this allows us to go from 2016-01-31 to 2016-02-29 back to 2016-03-31,
    while the more simple recur would be stuck at 2016-03-29.
    """
    new_x = x
    i = 0

    while not condition(new_x):
        i += 1
        new_x = operation(x, i)

    return new_x


def safe_date(y, m, d):
    """
    Returns date(y, m, d), returning the last day of the month if the value of
    d exceeds the number of days in the month.
    """
    days_in_month = monthrange(y, m)[1]
    return date(y, m, d if d <= days_in_month else days_in_month)


def increment_month(dt, m=1):
    """
    Advances dt by m months.
    """
    return safe_date(
        dt.year + (dt.month + m - 1) // 12, (dt.month + m - 1) % 12 + 1, dt.day
    )


def load_from_csv(filename, historical=False):
    # TODO: Grab this from the cards thing.
    # Does it replace the whole thing? Or just insert?
    pass


def save_to_csv(filename, historical=False):
    # TODO: Grab this from the cards thing.
    pass
