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
from freshdesk.models import Ticket

class TestTicketAPI(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = API(DOMAIN, API_KEY)

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
