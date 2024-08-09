from os import urandom, path


# Web Server
CSRF_ENABLED = True
SECRET_KEY = urandom(30)
PROPAGATE_EXCEPTIONS = True
REMEMBER_COOKIE_NAME = 'expense_token'      # Needs to be unique server-wide.

# SQLAlchemy
basedir = path.abspath(path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(path.join(basedir, 'app.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Authentication
AUTH_METHOD = 'LDAP'
AUTH_URI = None
LDAP_URI = 'ldap://YOUR.LDAP.URI'
LDAP_SEARCH_BASE = 'ou=????,dc=????,dc=????'

# Admin
ADMIN_USERS = ['LDAP.USER.ID.HERE']

# Expense Settings
LOCAL_CURRENCY = 'CAD'
LOCAL_SYMBOL = '$'
FRACTIONS_PER_UNIT = 100        # Number of cents in a dollar (or equivalent)
LOADING_GIF = True
CONFIRM_DELETION = True
DATE_FORMAT = '%Y-%m-%d'
PAGE_SIZE = 100

# Currency Conversion
# Current: https://github.com/fawazahmed0/exchange-api
# Can consider fallback to https://freecurrencyapi.com if necessary
RATE_URL = 'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/{src}.json'
SYMBOLS_URL = 'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies.json'
