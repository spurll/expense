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
* ldap3
* regex
* requests
* sqlalchemy

Configuration
-------------

You'll need to create a `config.py` file, which specifies details such as which LDAP
server to use. A sample configuration file can be found at `sample_config.py`.

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

* Shouldn't have to reload the entire table after an edit (nontrivial, because the row's
  location may change, but not impossible either)
* Invalid currencies should display warning to user as well as to console
* Error messages should have better debugging information (error type, stack trace)
* Error messages should be non-interrupting and auto-dismissing (then we can have success
  messages, too)
* Implement `controller.save_csv`

Known Bugs
----------

* Because of the way `justify-content` works, the title is often not quite centred...
* Adding/editing seems to be broken on Edge (name, value, and note are not passed)

Special Thanks
==============

Currency conversion provided by [exchangeratesapi.io](https://exchangeratesapi.io).

License Information
===================

Written by Gem Newman. [Website](http://spurll.com) | [GitHub](https://github.com/spurll/) | [Twitter](https://twitter.com/spurll)

This work is licensed under Creative Commons [BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/).

JQuery and JQuery UI elements included under the [MIT "Expat" License](https://opensource.org/licenses/MIT).

Remember: [GitHub is not my CV](https://blog.jcoglan.com/2013/11/15/why-github-is-not-your-cv/).
