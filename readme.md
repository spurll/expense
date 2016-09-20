Expense
=======

A web application that tracks expenses.

Usage
=====

Installation
------------

TODO

Requirements
------------

* flask
* flask-login
* flask-wtf
* flask-sqlalchemy
* sqlalchemy
* ldap3

TODO

Configuration
-------------

You'll need to create a `config.py` file, which specifies details such as which LDAP
server to use. A sample configuration file can be found at `sample_config.py`.

Starting the Server
-------------------

Start the server with `run.py`. By default it will be accessible at `localhost:9999`. To
make the server world-accessible or for other options, see `run.py -h`.

Implementation Plan
===================

Ability to edit in JavaScript (AJAX)? (Initially, just use POSTs. Have an edit link/icon
that, when clicked, makes the line editable and adds a submit button next to it to submit
the change. Only one line can be editable at a time, so I guess that'll have to remove the
"add" line as well.)

Typical spends (like bus/Tims/etc.) are just recurring things without due dates (top of
list)

Instructions to add future/recurring expenses
(Drop-down)

Must also support other currencies
Mark values with asterisk when approximate (different currency)
Easy to lock in the CAD value when it comes through


Layout
------

```
[Link to Expense History in Header]
[Fields to add a Current Expense]
[List of Current Expenses]
[List of Scheduled/Recurring/Template Expenses]
[Fields to add a Scheduled Expense]
```

Bugs and Feature Requests
=========================

Feature Requests
----------------

* Automated rolling snapshots every day

Known Bugs
----------

None

Special Thanks
==============

Currency conversion provided by [Fixer.io](https://fixer.io).

License Information
===================

Written by Gem Newman. [Website](http://spurll.com) | [GitHub](https://github.com/spurll/) | [Twitter](https://twitter.com/spurll)

This work is licensed under Creative Commons [BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/).

Remember: [GitHub is not my CV](https://blog.jcoglan.com/2013/11/15/why-github-is-not-your-cv/).

