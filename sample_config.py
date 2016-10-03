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

# LDAP
LDAP_URI = 'ldap://YOUR.LDAP.URI'
LDAP_SEARCH_BASE = 'ou=????,dc=????,dc=????'

ADMIN_USERS = ['LDAP.USER.ID.HERE']

# Expense Settings
LOCAL_CURRENCY = 'CAD'
LOCAL_SYMBOL = '$'
FRACTIONS_PER_UNIT = 100    # Number of cents in a dollar (or local equivalent)
LOADING_GIF = False
