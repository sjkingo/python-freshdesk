# python-freshdesk

A library for the [Freshdesk](http://freshdesk.com/) helpdesk system for Python 2.7 and 3.

It is written in Python and only requires 1 external dependency: `python-requests`.

## Installation

The easiest way to install is from PyPi inside a virtualenv:

1. Create the virtualenv (Python 3!) and activate it:

   ```
   $ virtualenv -p python3 cool_app
   $ cd cool_app && source bin/activate
   ```

2. Install from PyPi:

   ```
   $ pip install python-freshdesk
   ```

## Usage

Please note the domain and API key are not real and the example will not work
without changing these.

```python
>>> from freshdesk.api import API
>>> a = API('company.freshdesk.com', 'q8dnkjaS554Aol21dmnas9d92')
>>> a.list_open_tickets()
[<Ticket 'New ticket'>, <Ticket 'Some tests should be created'>, <Ticket 'Library needs to be uploaded to PyPi'>]
>>> a.list_deleted_tickets()
[<Ticket 'This is a sample ticket'>]
```

To see which attributes were loaded for a ticket:

```python
>>> ticket = a.get_ticket(4)
>>> repr(ticket)
"<Ticket 'I keep typing Freskdesk instead of Freshdesk!>"
>>> ticket._keys
set([u'status', u'source_name', u'ticket_type', u'updated_at', ...])
```

Attributes are automatically converted to native Python objects where appropriate:

```python
>>> a.list_open_tickets()[0].created_at
datetime.datetime(2014, 12, 5, 14, 7, 44)
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
