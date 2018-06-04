# python-freshdesk

[![Build Status](https://travis-ci.org/sjkingo/python-freshdesk.svg)](https://travis-ci.org/sjkingo/python-freshdesk)
[![Coverage Status](https://img.shields.io/coveralls/sjkingo/python-freshdesk.svg)](https://coveralls.io/r/sjkingo/python-freshdesk)
[![Latest version](https://img.shields.io/pypi/v/python-freshdesk.svg)](https://pypi.python.org/pypi/python-freshdesk)

A library for the [Freshdesk](http://freshdesk.com/) helpdesk system for Python 2.7 and 3.

There is support for a limited subset of features, using either Freshdesk API v1 or v2.

Support for the v1 API includes the following features:
* Getting a [Ticket](http://freshdesk.com/api#view_a_ticket) and filtering ticket lists
* Getting a [Contact/User/Customer](http://freshdesk.com/api#view_user)
* Viewing [timesheets](http://freshdesk.com/api#view_all_time_entry)

Support for the v2 API includes the following features:
* [Tickets](http://developer.freshdesk.com/api/#tickets)
  - [List](http://developer.freshdesk.com/api/#list_all_tickets)
  - [Get](http://developer.freshdesk.com/api/#view_a_ticket)
  - [Create](http://developer.freshdesk.com/api/#create_ticket)
  - [Update](http://developer.freshdesk.com/api/#update_ticket)
  - [Delete](http://developer.freshdesk.com/api/#delete_a_ticket)
  - Custom ticket fields (as of 1.1.1)
* [Comments](http://developer.freshdesk.com/api/#conversations) (known as Conversations in Freshdesk)
  - [List](http://developer.freshdesk.com/api/#list_all_ticket_notes)
  - [Create note](http://developer.freshdesk.com/api/#add_note_to_a_ticket)
  - [Create reply](http://developer.freshdesk.com/api/#reply_ticket)
* [Groups](http://developer.freshdesk.com/api/#groups)
  - [List](http://developer.freshdesk.com/api/#list_all_groups)
  - [Get](http://developer.freshdesk.com/api/#view_group)
* [Company](https://developers.freshdesk.com/api/#companies)
* [Roles](https://developers.freshdesk.com/api/#roles) - from 1.1.1
* [Agents](https://developers.freshdesk.com/api/#agents) - from 1.1.1

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

To find your API key, follow Freshdesk's step-by-step solution article
[How to find your API key](https://support.freshdesk.com/support/solutions/articles/215517).

By default, API v1 is used for backwards compatibility. To specify v1 or v2
explicitly:

```python
>>> a = API('company.freshdesk.com', 'q8dnkjaS554Aol21dmnas9d92', version=2)
```

The `API` class provides access to all the methods exposed by the Freshdesk API.

### Tickets (API v2)

The Ticket API is accessed by using the methods assigned to the `a.tickets`
instance. Tickets are loaded as instances of the `freshdesk.v2.models.Ticket`
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

Creating a ticket in Freshdesk can be done with the `create_ticket` method.
For example, we can create a new ticket like this:

```python
ticket = a.tickets.create_ticket('This is a sample ticket',
                                 email='example@example.com',
                                 description='This is the description of the ticket',
                                 tags=['example'])
```

The only positional argument is the subject, which is always required.

All other values are optional named arguments, which you can find in the
Freshdesk API documentation for [creating a ticket](http://developer.freshdesk.com/api/#create_ticket).

While all but subject are optional, you will need to specify at least one of:
`requester_id`, `email`, `facebook_id`, `phone` or `twitter_id` as the
requester of the ticket, or the request will fail.

Updating a ticket is similar to creating a ticket. The only differences are
that the ticket ID becomes the first positional argument, and subject becomes
an optional named argument.

In this example, we update the subject and set the priority of the ticket
as urgent.

```python
ticket = a.tickets.update_ticket(4,
                                 subject='This is an urgent ticket',
                                 priority=4)
```

The full list of named arguments you can pass can be found in the Freshdesk
API documentation for [updating a ticket](http://developer.freshdesk.com/api/#update_ticket).

To delete a ticket, just pass the ticket ID value to the `delete_ticket` method:

```python
a.tickets.delete_ticket(4)
```

### Comments (API v2)

To view comments on a ticket (note or reply), use the `list_comments` method, from
the comments module, and pass it the ticket number:

```python
>>> a.comments.list_comments(4)
[<Comment for <Ticket 'Some tests should be created'>>]
>>> ticket.comments[0]
'We could use Travis CI'
```

The original comment (called "description" in Freshdesk) is available on the `Ticket` instance:

```python
>>> ticket.description
'nose is a good suite'
```

If you want to add a comment to an existing ticket, you can do it via a note
or a reply.

The differences between notes and replies are that notes can be private
(only visible to the agents, default). Replies are intended to be comments
that are sent to the user (e.g. as an email).

To create a note:
```python
>>> comment = a.comments.create_note(4,
                                     'This is a public note',
                                     private=False)
'<Comment for Ticket #4>'
```

To create a reply:
```python
>>> a.comments.create_reply(4, 'This is the body of a reply')
'<Comment for Ticket #4>'
```

The documentaion for [creating a reply](http://developer.freshdesk.com/api/#reply_ticket)
and [creating a note](http://developer.freshdesk.com/api/#add_note_to_a_ticket)
will provide details of the fields available, which you can pass as named
arguments.

In both methods, the ticket ID and body must be given as positional arguments.


### Contacts/Users (API v1)

Freshdesk mixes up the naming of contacts and users, depending on whether they are an agent or not.
`python-freshdesk` simply calls them all contacts and are represented as `Contact` instances:

```python
>>> repr(a.contacts.get_contact('1234'))
"<Contact 'Rachel'>"
```

### Timesheets (API v1)

You can view all timesheets:

```python
>>> a.timesheets.get_all_timesheets()
[<Timesheet Entry 1>, <Timesheet Entry 2, ...]
```

Or filter by ticket number:

```python
>>> a.timesheets.get_timesheet_by_ticket(4)
[<Timesheet Entry 7>]
```
