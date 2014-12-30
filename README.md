# freshdesk-api

A library for the [Freshdesk](http://freshdesk.com/) helpdesk system for Python 3.

## Installation

The easiest way to install is from PyPi inside a virtualenv:

1. Create the virtualenv (Python 3!) and activate it:

   ```
   $ virtualenv -p python3 cool_app
   $ cd cool_app && source bin/activate
   ```

2. Install from PyPi:

   `$ pip install python-freshdesk`

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
