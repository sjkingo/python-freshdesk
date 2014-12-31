# python-freshdesk

A library for the [Freshdesk](http://freshdesk.com/) helpdesk system for Python 2.7 and 3.

It is written in Python and only requires 1 external dependency: `python-requests`.

Currently it only supports the [Ticket API](http://freshdesk.com/api#view_a_ticket).

[![Build Status](https://travis-ci.org/sjkingo/python-freshdesk.svg)](https://travis-ci.org/sjkingo/python-freshdesk)

## Installation

The easiest way to install is from [PyPi](https://pypi.python.org/pypi/python-freshdesk) inside a virtualenv:

1. Create the virtualenv (Python 3!) and activate it:

   ```
   $ virtualenv -p python3 cool_app
   $ cd cool_app && source bin/activate
   ```

2. Install from PyPi:

   ```
   $ pip install python-freshdesk
   ```

3. Optionally, run the test suite:

   ```
   $ pip install nose
   $ nosetests
   ```

## Usage

Please note the domain and API key are not real and the example will not work
without changing these.

```python
>>> from freshdesk.api import API
>>> a = API('company.freshdesk.com', 'q8dnkjaS554Aol21dmnas9d92')
```

The `API` class provides access to all the methods exposed by the Freshdesk API.

### Tickets

The Ticket API is accessed by using the methods assigned to the `a.tickets`
instance. Tickets are loaded as instances of the `freshdesk.models.Ticket`
class, and can be iterated over:

```python
>>> a.tickets.list_open_tickets()
[<Ticket 'New ticket'>, <Ticket 'Some tests should be created'>, <Ticket 'Library needs to be uploaded to PyPi'>]
>>> a.tickets.list_deleted_tickets()
[<Ticket 'This is a sample ticket'>]
```

To see which attributes were loaded for a ticket:

```python
>>> ticket = a.tickets.get_ticket(4)
>>> repr(ticket)
"<Ticket 'I keep typing Freskdesk instead of Freshdesk!>"
>>> ticket._keys
set([u'status', u'source_name', u'ticket_type', u'updated_at', ...])
```

Attributes are automatically converted to native Python objects where appropriate:

```python
>>> a.tickets.list_open_tickets()[0].created_at
datetime.datetime(2014, 12, 5, 14, 7, 44)
```

Or converted from indexes to their descriptions:

```python
>>> ticket.priority
'medium'
>>> ticket.status
'closed'
>>> ticket.source
'phone'
```

Viewing comments on a ticket are as simple as looking at the `Ticket.comments` list:

```python
>>> ticket.comments
[<Comment for <Ticket 'Some tests should be created'>>]
>>> ticket.comments[0]
'We could use Travis CI'
```

The original comment (called "description" in Freshdesk) is available on the `Ticket` instance:

```python
>>> ticket.description
'nose is a good suite'
```
