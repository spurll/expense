Expense
=======

A web application that tracks expenses.

Usage
=====

Requirements
------------

* flask
* flask-login
* flask-wtf
* flask-sqlalchemy
* sqlalchemy
* ldap3

Configuration
-------------

You'll need to create a `config.py` file, which specifies details such as which LDAP
server to use. A sample configuration file can be found at `sample_config.py`.

Starting the Server
-------------------

Start the server with `run.py`. By default it will be accessible at `localhost:9999`. To
make the server world-accessible or for other options, see `run.py -h`.

Bugs and Feature Requests
=========================

Feature Requests
----------------

* Automated rolling snapshots every day
* Invalid currencies should display warning to user as well as to console
* Error messages should have better debugging information (error type, stack trace)
* Error messages should be non-interrupting and auto-dismissing (then we can have success
  messages, too)
* Implement `controller.save_csv`
* Move efficient updates: just remove the appropriate rows from the tables (rather than
  reloading the whole thing)
* Probably need pagination for the history page (it can get *huge*)

Known Bugs
----------

* Because of the way information is sent via GET requests, it's impossible remove
  recurrence from an item (because it requires setting the value to "")
* When editing an item, currency information is not populated (Javascript should have
  access to the value of LOCAL_CURRENCY and should compare the title text to see if it's
  relevant)

Special Thanks
==============

Currency conversion provided by [Fixer.io](https://fixer.io).

License Information
===================

Written by Gem Newman. [Website](http://spurll.com) | [GitHub](https://github.com/spurll/) | [Twitter](https://twitter.com/spurll)

This work is licensed under Creative Commons [BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/).

JQuery and JQuery UI elements included under the [MIT "Expat" License](https://opensource.org/licenses/MIT).

Remember: [GitHub is not my CV](https://blog.jcoglan.com/2013/11/15/why-github-is-not-your-cv/).
