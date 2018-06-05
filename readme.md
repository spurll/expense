Expense
=======

A web application that tracks expenses.

![Screenshot](/screenshots/exp.png?raw=true)

Usage
=====

Requirements
------------

* flask
* flask-login
* flask-wtf
* flask-sqlalchemy
* sqlalchemy
* requests
* ldap3

Configuration
-------------

You'll need to create a `config.py` file, which specifies details such as which LDAP
server to use. A sample configuration file can be found at `sample_config.py`.

You will also need to sign up for an account at [Fixer.io](https://fixer.io), which
handles currency conversions. Once you've done so, add your API key to `config.py`.

Starting the Server
-------------------

Start the server with `run.py`. By default it will be accessible at `localhost:9999`. To
make the server world-accessible or for other options, see `run.py -h`.

If you're having trouble configuring your sever, I wrote a
[blog post](http://blog.spurll.com/2015/02/configuring-flask-uwsgi-and-nginx.html)
explaining how you can get Flask, uWSGI, and Nginx working together.

Bugs and Feature Requests
=========================

Feature Requests
----------------

* Invalid currencies should display warning to user as well as to console
* Error messages should have better debugging information (error type, stack trace)
* Error messages should be non-interrupting and auto-dismissing (then we can have success
  messages, too)
* Implement `controller.save_csv`

Known Bugs
----------

* Adding/editing seems to be broken on Edge (name, value, and note are not passed)
* Clicking the "edit" button when another field is already being edited causes problems;
  can probably be fixed by calling hte "cancel" button's functions first
* Because of the way information is sent via GET requests, it's impossible remove
  recurrence from an item (because it requires setting the value to "")

Special Thanks
==============

Currency conversion provided by [Fixer.io](https://fixer.io).

License Information
===================

Written by Gem Newman. [Website](http://spurll.com) | [GitHub](https://github.com/spurll/) | [Twitter](https://twitter.com/spurll)

This work is licensed under Creative Commons [BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/).

JQuery and JQuery UI elements included under the [MIT "Expat" License](https://opensource.org/licenses/MIT).

Remember: [GitHub is not my CV](https://blog.jcoglan.com/2013/11/15/why-github-is-not-your-cv/).
