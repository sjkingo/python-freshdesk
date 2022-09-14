# python-freshdesk

[![Build Status](https://travis-ci.org/sjkingo/python-freshdesk.svg)](https://travis-ci.org/sjkingo/python-freshdesk)
[![Coverage Status](https://img.shields.io/coveralls/sjkingo/python-freshdesk.svg)](https://coveralls.io/r/sjkingo/python-freshdesk)
[![Latest version](https://img.shields.io/pypi/v/python-freshdesk.svg)](https://pypi.python.org/pypi/python-freshdesk)

This is a library for the [Freshdesk](http://freshdesk.com/) helpdesk system for Python 2.7 and 3.6+.

It includes the following features from the [Freshdesk v2 API](https://developers.freshdesk.com/api/):

* [Tickets](http://developer.freshdesk.com/api/#tickets)
  - [Get](http://developer.freshdesk.com/api/#view_a_ticket)
  - [Create](http://developer.freshdesk.com/api/#create_ticket)
  - [Update](http://developer.freshdesk.com/api/#update_ticket)
  - [Delete](http://developer.freshdesk.com/api/#delete_a_ticket)
  - [Create OutBound Email](http://developer.freshdesk.com/api/#create_outbound_email)
  - [List](http://developer.freshdesk.com/api/#list_all_tickets)
  - [Filter](https://developer.freshdesk.com/api/#filter_tickets) (from 1.2.6)
  - [List Time Entries](https://developers.freshdesk.com/api/#list_all_ticket_timeentries) (from 1.2.4)
  - Custom ticket fields (from 1.1.1)
* [Ticket Fields](http://developer.freshdesk.com/api/#ticket_fields)
    - [List](http://developer.freshdesk.com/api/#list_all_ticket_fields)
* [Comments](http://developer.freshdesk.com/api/#conversations) (known as Conversations in Freshdesk)
  - [List](http://developer.freshdesk.com/api/#list_all_ticket_notes)
  - [Create note](http://developer.freshdesk.com/api/#add_note_to_a_ticket)
  - [Create reply](http://developer.freshdesk.com/api/#reply_ticket)
* [Groups](http://developer.freshdesk.com/api/#groups)
  - [List](http://developer.freshdesk.com/api/#list_all_groups)
  - [Get](http://developer.freshdesk.com/api/#view_group)
* [Contacts](http://developer.freshdesk.com/api/#contacts)
    - [Get](http://developer.freshdesk.com/api/#view_contact)
    - [List](http://developer.freshdesk.com/api/#list_all_contacts)
    - [Create](http://developer.freshdesk.com/api/#create_contact)
    - [Update](http://developer.freshdesk.com/api/#update_contact) (from 1.2.3)
    - [Filter](https://developers.freshdesk.com/api/#filter_contacts) (from 1.3.9)
    - [Delete](http://developer.freshdesk.com/api/#delete_contact)
    - [Restore](http://developer.freshdesk.com/api/#restore_contact) (from 1.2.3)
    - [Make agent](http://developer.freshdesk.com/api/#make_agent)
* [Company](https://developers.freshdesk.com/api/#companies)
    - [Get](http://developer.freshdesk.com/api/#view_company)
    - [List](http://developer.freshdesk.com/api/#list_all_companies) (from 1.2.8)
    - [Filter](https://developers.freshdesk.com/api/#filter_companies) (from 1.3.2)
    - [Delete](https://developers.freshdesk.com/api/#delete_company) (from 1.3.5)
    - [Create](https://developers.freshdesk.com/api/#create_company) (from 1.3.6)
    - [Update](https://developers.freshdesk.com/api/#update_company) (from 1.3.6)
* [Roles](https://developers.freshdesk.com/api/#roles) (from 1.1.1)
    - [Get](http://developer.freshdesk.com/api/#view_role)
    - [List](http://developer.freshdesk.com/api/#list_role)
* [Agents](https://developers.freshdesk.com/api/#agents) (from 1.1.1)
    - [Get](http://developer.freshdesk.com/api/#view_agent)
    - [List](http://developer.freshdesk.com/api/#list_all_agents)
    - [Update](http://developer.freshdesk.com/api/#update_agent)
    - [Delete](http://developer.freshdesk.com/api/#delete_agent)
* [Solutions](http://developer.freshdesk.com/api/#solutions) (from master)
    - [Solution Category](https://developer.freshdesk.com/api/#solution_category_attributes) (from 1.3.8)
      - Get
      - Get Translated
      - List
      - List Translated
      - Create
      - Create Translated
      - Update
      - Update Translated
      - Delete
    - [Solution Folder](https://developer.freshdesk.com/api/#solution_folder_attributes) (from 1.3.8)
      - Get
      - Get Translated
      - List
      - List Translated
      - Create
      - Create Translated
      - Update
      - Update Translated
      - Delete
    - [Solution Article](https://developer.freshdesk.com/api/#solution_article_attributes) (from 1.3.8)
      - Get
      - Get Translated
      - List
      - List Translated
      - Create
      - Create Translated
      - Update
      - Update Translated
      - Delete


From version 1.3.0, this library uses the Freshdesk v2 API by default.

## Installation

The easiest way to install is from [PyPi](https://pypi.python.org/pypi/python-freshdesk) inside a virtualenv:

1. Create the virtualenv (Python 2.7 and 3.6+ supported) and activate it:

   ```
   $ virtualenv cool_app
   $ cd cool_app && source bin/activate
   ```

2. Install from PyPi:

   ```
   $ pip install python-freshdesk
   ```

3. Optionally, run the test suite:

   ```
   $ pip install pytest
   $ pytest
   ```

## Usage

Please note the domain and API key are not real and the example will not work without changing these.

```python
>>> from freshdesk.api import API
>>> a = API('company.freshdesk.com', 'q8dnkjaS554Aol21dmnas9d92')
```

To find your API key, follow Freshdesk's step-by-step solution article
[How to find your API key](https://support.freshdesk.com/support/solutions/articles/215517).

The `API` class provides access to all the methods exposed by the Freshdesk API.

Optionally, the API can be given SSL verification and/or proxy settings to obey for all requests:

```python
>>> a = API('company.freshdesk.com', 'q8dnkjaS554Aol21dmnas9d92', verify=False)
```

```python
>>> proxies = {
...     'http': 'http://example.proxy:8000',
...     'https': 'https://example.proxy:8443'
... }
>>> a = API('company.freshdesk.com', 'q8dnkjaS554Aol21dmnas9d92', proxies=proxies)
```

### Tickets

The Ticket API is accessed by using the methods assigned to the `a.tickets` instance. Tickets are loaded as instances
of the `freshdesk.v2.models.Ticket` class, and can be iterated over:

```python
>>> a.tickets.list_tickets()
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
>>> a.tickets.list_tickets()[0].created_at
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

You can get additional details of the ticket in the response using extra arguments (from 1.3.5).

Please take a look at the FreshDesk documentation for more details: [View a Ticket](http://developer.freshdesk.com/api/#view_a_ticket)

```python
>>> ticket = a.tickets.get_ticket(4, "conversation", "requester", "company", "stats")
>>> ticket.stats
{'agent_responded_at': '2020-06-26T01:23:39Z',
 'requester_responded_at': '2020-06-25T23:10:15Z',
 'first_responded_at': '2020-06-17T20:23:43Z',
 'status_updated_at': '2020-07-24T15:35:21Z',
 'reopened_at': None,
 'resolved_at': '2020-07-24T15:35:21Z',
 'closed_at': None,
 'pending_since': None}
```

Creating a ticket can be done by calling `create_ticket()`:

```python
ticket = a.tickets.create_ticket('This is a sample ticket',
                                 email='example@example.com',
                                 description='This is the description of the ticket',
                                 tags=['example'])
```

To create a ticket with attachments, pass a list of fully quilified file paths with key name `attachments`:

```python
ticket = a.tickets.create_ticket('This is a sample ticket',
                                 email='example@example.com',
                                 description='This is the description of the ticket',
                                 tags=['example'],
                                 attachments=[
                                 '/path/to/file1',
                                 '/path/to/file2']
                                 )
```

The only positional argument is the subject, which is always required.

You will need to specify at least one of: `requester_id`, `email`, `facebook_id`, `phone` or `twitter_id` as the
requester of the ticket, or the request will fail. All other [keyword arguments](http://developer.freshdesk.com/api/#create_ticket) are optional.

You can get the list of tickets by calling `list_tickets()`:

```python
ticket = a.tickets.list_tickets(filter_name=None, updated_since='2014-01-01T00:00:00.000Z', page=1, per_page=10)
``` 

All arguments given above are optional.

By default the `new_and_my_open` filter is used. If you want to list all the tickets without any filter, pass
`filter_name=None`.

Only the tickets that have been created within the past 30 days will be returned by default.
For fetching older tickets, use the `updated_since` argument to pass a datetime in isoformat (from 1.3.3).

Pagination is supported. If `page` argument is not passed, all pages are fetched, else the specified page is returned.

Updating a ticket is similar to creating a ticket. The only differences are that the ticket ID becomes the first
positional argument, and subject becomes an optional named argument.

In this example, we update the subject and set the priority of the ticket as urgent:

```python
ticket = a.tickets.update_ticket(4,
                                 subject='This is an urgent ticket',
                                 priority=4)
```

The full list of named arguments you can pass can be found in [updating a ticket](http://developer.freshdesk.com/api/#update_ticket).

To delete a ticket, just pass the ticket ID value to `delete_ticket()`:

```python
a.tickets.delete_ticket(4)
```

### Ticket Fields

To view ticket fields, call `list_ticket_fields()` with a field type:

```python
>>> a.ticket_fields.list_ticket_fields(type='default_requester')
[<TicketFields Requester Email of Requester >, <TicketFields Type Type of Ticket >]

```

### Comments

To view comments on a ticket (note or reply), pass the ticket number to `list_comments()`:

```python
>>> a.comments.list_comments(4)
[<Comment for <Ticket 'Some tests should be created'>>]
>>> ticket.comments[0]
'We could use Travis CI'
```

Pagination is supported. If `page` option is not specified, then all the pages are fetched, else specified page is returned. 

The original comment (called "description" in Freshdesk) is available on the `Ticket` instance:

```python
>>> ticket.description
'nose is a good suite'
```

If you want to add a comment to an existing ticket, you can do it via a note or a reply.

The differences between notes and replies are that notes can be private (only visible to the agents, default).
Replies are intended to be comments that are sent to the user (e.g. as an email).

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

The documentaion for [creating a reply](http://developer.freshdesk.com/api/#reply_ticket) and [creating a
note](http://developer.freshdesk.com/api/#add_note_to_a_ticket) will provide details of the fields available, which
you can pass as named arguments.

In both methods, the ticket ID and body must be given as positional arguments.

### Contacts

Freshdesk mixes up the naming of contacts and users, depending on whether they are an agent or not.
`python-freshdesk` simply calls them all contacts and are represented as `Contact` instances:

```python
>>> repr(a.contacts.get_contact(1234))
"<Contact 'Rachel'>"
```

Get the list of contacts using:

```python
>>> repr(a.contacts.list_contacts(page=1, per_page=10))
["<Contact 'Rachel'>"]
```

Pagination is supported. If `page` option is not specified, then all the pages are fetched, else specified page is
returned. Contact can be filtered using name or email by passing the filter as `email=abc@xyz.com` or
`mobile=123792182138` or `state=deleted`

Other supported methods are `create_contact`, `update_contact`, `soft_delete_contact`, `permanently_delete_contact`,
`restore_contact`

To convert a contact to an agent, use:

```python
>>> repr(a.contacts.make_agent(1))
["<Agent 'Rachel'>"]
```

### Agents

To get a specific agent instance, use:

```python
>>> repr(a.agents.get_agent(1234))
"<Agent 'Rachel'>"
```

You can list all agents by calling `list_agents()`:

```python
>>> repr(a.agents.list_agents(page=1, per_page=10))
["<Agent 'Rachel'>"]
```

Pagination is supported. If `page` option is not specified, then all the pages are fetched, else specified page is
returned. Agent can be filtered using name or email by passing the filter as `email=abc@xyz.com` or
`mobile=123792182138`

Other supported methods are `update_agent`, `delete_agent`

### Groups

To get the list of groups, use:

```python
>>> repr(a.groups.list_groups(page=1, per_page=10))
["<Group 'Service Managers'>"]
```

Pagination is supported. If `page` option is not specified, then all the pages are fetched, else specified page is returned.
 
To get a group, use:

```python
>>> repr(a.groups.get_group(1))
["<Group 'Service Managers'>"]
``` 

### Companies

To get the list of companies, use:

```python
>>> repr(a.companies.list_companies(page=1, per_page=10))
["<Company 'Super Nova'>"]
```

Pagination is supported. If `page` option is not specified, then all the pages are fetched, else specified page is returned.
 
To get a company, use:

```python
>>> repr(a.companies.get_company(1))
"<Company 'Super Nova'>"
``` 

[Filtering is also supported](https://developers.freshdesk.com/api/#filter_companies):
```python
a.companies.filter_companies(query="updated_at:>'2020-07-12'")
```

To delete a company (from 1.3.5), call `delete_company()` and pass the Freshdesk company ID.

## Solutions

### Solution Categories

To get the list of solution categories, use:

```python
>>> repr(a.solutions.categories.list_categories())
["<SolutionCategory 'General Category' #2>"]
```

To get the translated solution categories, use:

```python
>>> repr(a.solutions.categories.list_categories_translated('fr'))
["<SolutionCategory 'Catégorie générale' #2>"]
```

### Solution Folders

To get the list of folders from a solution category, use:

```python
>>> repr(a.solutions.folders.list_from_category(2))
["<SolutionFolder 'Getting Started' #3>"]
```

To get the list of translated folders from a solution category, use:

```python
>>> repr(a.solutions.folders.list_from_category_translated(2, 'fr'))
["<SolutionFolder 'Commencer' #3>"]
```
### Solution Articles

To get list of solution articles within a folder, use:

```python
>>> repr(a.solutions.articles.list_from_foldery(3))
["<SolutionArticle 'Changing account details' #4>"]
```

To get list of solution translatied articles within a folder, use:

```python
>>> repr(a.solutions.articles.list_from_foldery_translated(3, 'fr'))
["<SolutionArticle 'Modifier les détails du compte' #4>"]
```

To get a specific article by number, use:

```python
>>> repr(a.solutions.articles.get_article(5))
["<SolutionArticle 'Adding a payment method' #5>"]
```

To get a translated solution article, use:

```python
>>> repr(a.solutions.articles.get_article_translated(5, 'fr'))
["<SolutionArticle 'Ajouter un moyen de paiement' #5>"]
```

## Credits

Thank you to all the people who have worked on this library and made it great for everyone.
