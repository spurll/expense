from datetime import date
from calendar import monthrange
import requests

from expense import app


RATE_URL = app.config.get('RATE_URL')
SYMBOLS_URL = app.config.get('SYMBOLS_URL')
CENTS = app.config.get('FRACTIONS_PER_UNIT', 100)
LOCAL = app.config.get('LOCAL_CURRENCY')

rate_cache = {}
symbols_cache = []
errors = []


def error(e):
    print(e)
    errors.append(str(e))


def get_errors():
    err = errors.copy()
    errors.clear()
    return err


def to_fractional(value):
    # Rounding is required because of imprecise represenation of floating point
    # numbers (e.g., 2.53 * 100 results in 252.99999999999997, which int will
    # truncate to 252).
    return int(round(value * CENTS))


def to_major(value):
    return float(value) / CENTS


def format_local(value, original_currency=LOCAL):
    """
    Converts a local currency value (in cents) in a readable string format.
    """
    if value is None:
        return '—'

    fmt = '{n_open}{symbol}{value:,.2f}{converted}{n_close}'
    return fmt.format(
        n_open='(' if value < 0 else '',
        symbol=app.config.get('LOCAL_SYMBOL', '$'),
        value=abs(to_major(value)),
        converted='' if original_currency == LOCAL else '*',
        n_close=')' if value < 0 else ''
    )


def format_raw(value, currency=LOCAL):
    """
    Converts a currency value (in cents) in a raw-ish string format.
    """
    if value is None:
        return ''

    fmt = '{value:,.2f} {currency}'
    return fmt.format(value=to_major(value), currency=currency)


def list_currencies():
    """
    Lists all valid currencies (those supported by the exchange rate provider).
    """
    if SYMBOLS_URL and not symbols_cache:
        try:
            r = requests.get(SYMBOLS_URL)
        except Exception as e:
            error(e)
            return symbols_cache

        if r.status_code == 200:
            symbols_cache.append(r.json().get('base'))
            symbols_cache.extend(r.json().get('rates', {}).keys())
            symbols_cache.sort()

            # Move local currency to the top of the list.
            if LOCAL in symbols_cache:
                symbols_cache.insert(
                    0, symbols_cache.pop(symbols_cache.index(LOCAL))
                )

            if not symbols_cache:
                error(f'No currency symbols found. Request returned: {r.text}')

        else:
            error(f'No currency symbols found. Request returned: {r.text}')

    return symbols_cache


def convert_currency(value, src, dst, d):
    """
    Converts value between two currencies using the conversion rate for date.
    """
    return value * (conversion_rate(src, dst, d) if src != dst else 1)


def conversion_rate(src, dst, d):
    """
    Returns the historical conversion rate between two currencies.
    """
    request = RATE_URL.format(date=d, src=src, dst=dst) if RATE_URL else None

    if request and request not in rate_cache:
        try:
            r = requests.get(request)
        except Exception as e:
            error(e)
            return 1

        if r.status_code == 200:
            rate = r.json().get('rates', {}).get(dst)

            if rate is not None:
                rate_cache[request] = rate
            else:
                error(f'No rate for {dst} found. Request returned: {r.text}')

        else:
            error(f'No rate for {dst} found. Request returned: {r.text}')

    return rate_cache.get(request, 1)


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

