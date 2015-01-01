"""
Test suite for python-freshdesk.

We test against a dummy helpdesk created for these tests only. It is:
http://pythonfreshdesk.freshdesk.com/
"""

DOMAIN = 'pythonfreshdesk.freshdesk.com'
API_KEY = 'MX4CEAw4FogInimEdRW2'

import datetime
import json
import re
import os.path
from unittest import TestCase

from freshdesk.api import API
from freshdesk.models import Ticket, Comment

class MockedAPI(API):
    def __init__(self, *args):
        self.resolver = {
            re.compile(r'tickets/filter/all_tickets\?format=json&page=1'): self.read_test_file('all_tickets.json'),
            re.compile(r'tickets/filter/new_my_open\?format=json&page=1'): self.read_test_file('all_tickets.json'),
            re.compile(r'tickets/filter/spam\?format=json&page=1'): [],
            re.compile(r'tickets/filter/deleted\?format=json&page=1'): [],
            re.compile(r'tickets/1.json'): self.read_test_file('ticket_1.json'),
            re.compile(r'.*&page=2'): [],
        }
        super(MockedAPI, self).__init__(*args)

    def read_test_file(self, filename):
        path = os.path.join(os.path.dirname(__file__), 'sample_json_data', filename)
        return json.loads(open(path, 'r').read())

    def _get(self, url, *args, **kwargs):
        for pattern, json in self.resolver.items():
            if pattern.match(url):
                return json

        # No match found, raise 404
        from requests.exceptions import HTTPError
        raise HTTPError('404: mocked_api_get() has no pattern for \'{}\''.format(url))

class TestAPIClass(TestCase):
    def test_api_prefix(self):
        api = API('test_domain', 'test_key')
        self.assertEqual(api._api_prefix, 'http://test_domain/helpdesk/')
        api = API('test_domain/', 'test_key')
        self.assertEqual(api._api_prefix, 'http://test_domain/helpdesk/')

    def test_403_error(self):
        api = API(DOMAIN, 'invalid_api_key')
        from requests.exceptions import HTTPError
        with self.assertRaises(HTTPError):
            api.tickets.get_ticket(1)

    def test_404_error(self):
        api = API('ticketus.org', 'invalid_api_key')
        from requests.exceptions import HTTPError
        with self.assertRaises(HTTPError):
            api.tickets.get_ticket(1)

class TestTicket(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = MockedAPI(DOMAIN, API_KEY)
        cls.ticket = cls.api.tickets.get_ticket(1)

    def test_str(self):
        self.assertEqual(str(self.ticket), 'This is a sample ticket')

    def test_repr(self):
        self.assertEqual(repr(self.ticket), '<Ticket \'This is a sample ticket\'>')

    def test_get_ticket(self):
        self.assertIsInstance(self.ticket, Ticket)
        self.assertEqual(self.ticket.display_id, 1)
        self.assertEqual(self.ticket.subject, 'This is a sample ticket')
        self.assertEqual(self.ticket.description, 'This is a sample ticket, feel free to delete it.')

    def test_ticket_priority(self):
        self.assertEqual(self.ticket._priority, 1)
        self.assertEqual(self.ticket.priority, 'low')

    def test_ticket_status(self):
        self.assertEqual(self.ticket._status, 2)
        self.assertEqual(self.ticket.status, 'open')

    def test_ticket_source(self):
        self.assertEqual(self.ticket._source, 2)
        self.assertEqual(self.ticket.source, 'portal')

    def test_ticket_datetime(self):
        self.assertIsInstance(self.ticket.created_at, datetime.datetime)
        self.assertIsInstance(self.ticket.updated_at, datetime.datetime)

    def test_all_tickets(self):
        tickets = self.api.tickets.list_all_tickets()
        self.assertIsInstance(tickets, list)
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].display_id, self.ticket.display_id)

    def test_open_tickets(self):
        tickets = self.api.tickets.list_open_tickets()
        self.assertIsInstance(tickets, list)
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].display_id, self.ticket.display_id)

    def test_deleted_tickets(self):
        tickets = self.api.tickets.list_deleted_tickets()
        self.assertIsInstance(tickets, list)
        self.assertEqual(len(tickets), 0)

    def test_spam_tickets(self):
        tickets = self.api.tickets.list_tickets(filter_name='spam')
        self.assertIsInstance(tickets, list)
        self.assertEqual(len(tickets), 0)

    def test_default_filter_name(self):
        tickets = self.api.tickets.list_tickets()
        self.assertIsInstance(tickets, list)
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].display_id, self.ticket.display_id)

class TestComment(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = MockedAPI(DOMAIN, API_KEY)
        cls.ticket = cls.api.tickets.get_ticket(1)

    def test_comments_list(self):
        self.assertIsInstance(self.ticket.comments, list)
        self.assertEqual(len(self.ticket.comments), 1)
        self.assertIsInstance(self.ticket.comments[0], Comment)

    def test_comment_str(self):
        self.assertEqual(str(self.ticket.comments[0]), 'This is a reply.')

    def test_comment_repr(self):
        self.assertEqual(repr(self.ticket.comments[0]), '<Comment for <Ticket \'This is a sample ticket\'>>')
