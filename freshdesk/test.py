"""
Test suite for python-freshdesk.

We test against a dummy helpdesk created for these tests only. It is:
http://pythonfreshdesk.freshdesk.com/
"""

DOMAIN = 'pythonfreshdesk.freshdesk.com'
API_KEY = 'MX4CEAw4FogInimEdRW2'

import datetime
from unittest import TestCase

from freshdesk.api import API
from freshdesk.models import Ticket, Comment

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

class TestTicketAPI(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = API(DOMAIN, API_KEY)

    def test_str(self):
        ticket = self.api.tickets.get_ticket(1)
        self.assertEqual(str(ticket), 'This is a sample ticket')

    def test_repr(self):
        ticket = self.api.tickets.get_ticket(1)
        self.assertEqual(repr(ticket), '<Ticket \'This is a sample ticket\'>')

    def test_get_ticket(self):
        ticket = self.api.tickets.get_ticket(1)
        self.assertIsInstance(ticket, Ticket)
        self.assertEqual(ticket.display_id, 1)
        self.assertEqual(ticket.subject, 'This is a sample ticket')
        self.assertEqual(ticket.description, 'This is a sample ticket, feel free to delete it.')

    def test_ticket_priority(self):
        ticket = self.api.tickets.get_ticket(1)
        self.assertEqual(ticket._priority, 1)
        self.assertEqual(ticket.priority, 'low')

    def test_ticket_status(self):
        ticket = self.api.tickets.get_ticket(1)
        self.assertEqual(ticket._status, 2)
        self.assertEqual(ticket.status, 'open')

    def test_ticket_source(self):
        ticket = self.api.tickets.get_ticket(1)
        self.assertEqual(ticket._source, 2)
        self.assertEqual(ticket.source, 'portal')

    def test_ticket_datetime(self):
        ticket = self.api.tickets.get_ticket(1)
        self.assertIsInstance(ticket.created_at, datetime.datetime)
        self.assertIsInstance(ticket.updated_at, datetime.datetime)

    def test_all_tickets(self):
        tickets = self.api.tickets.list_all_tickets()
        ticket1 = self.api.tickets.get_ticket(1)
        self.assertIsInstance(tickets, list)
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].display_id, ticket1.display_id)

    def test_open_tickets(self):
        tickets = self.api.tickets.list_open_tickets()
        ticket1 = self.api.tickets.get_ticket(1)
        self.assertIsInstance(tickets, list)
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].display_id, ticket1.display_id)

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
        ticket1 = self.api.tickets.get_ticket(1)
        self.assertIsInstance(tickets, list)
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].display_id, ticket1.display_id)

class TestComment(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = API(DOMAIN, API_KEY)
        cls.ticket = cls.api.tickets.get_ticket(1)

    def test_comments_list(self):
        self.assertIsInstance(self.ticket.comments, list)
        self.assertEqual(len(self.ticket.comments), 1)
        self.assertIsInstance(self.ticket.comments[0], Comment)

    def test_comment_str(self):
        self.assertEqual(str(self.ticket.comments[0]), 'This is a reply.')

    def test_comment_repr(self):
        self.assertEqual(repr(self.ticket.comments[0]), '<Comment for <Ticket \'This is a sample ticket\'>>')
