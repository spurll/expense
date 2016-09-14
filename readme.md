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

Recurring things that can be activated below current things

Recurring items can recur on a schedule (in which the due date is incremented) or just
"recur" (due date isn't changed at all, and is probably blank)

Typical spends (like bus/Tims/etc.) are just recurring things without due dates (top of
list)

Load from save to CSV (reuse code from cards)

Instructions to add recurring expenses
(Drop-down)

Must also support other currencies
Allow specifying the currency from this list: {"AUD":1.3106,"BGN":1.7527,"BRL":3.266,"CAD":1.2909,"CHF":0.97885,"CNY":6.6785,"CZK":24.215,"DKK":6.6686,"GBP":0.74859,"HKD":7.7554,"HRK":6.7158,"HUF":277.62,"IDR":13117.0,"ILS":3.7642,"INR":66.491,"JPY":103.41,"KRW":1105.6,"MXN":18.523,"MYR":4.0815,"NOK":8.2546,"NZD":1.3626,"PHP":46.588,"PLN":3.8882,"RON":3.989,"RUB":64.827,"SEK":8.5456,"SGD":1.3559,"THB":34.66,"TRY":2.9412,"ZAR":14.205,"EUR":0.89614}
On-the-fly converstion using fixer.io: http://api.fixer.io/latest?base=USD&symbol=CAD
Use the exchange rate for the appropriate date: http://api.fixer.io/2016-01-03?base=USD&symbol=CAD
Mark with asterisk when approximate
Easy to lock in the CAD value when it comes through
Table has CAD, mouse-over text indicating the raw value in whatever other currency

Make the symbol a dollar sign

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

None

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

