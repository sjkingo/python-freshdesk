import datetime
import json
import re
import os.path
import responses
from unittest import TestCase

from freshdesk.v1.api import API
from freshdesk.v1.models import Ticket, Comment, Contact, Customer, TimeEntry, Agent

"""
Test suite for python-freshdesk.

We test against a dummy helpdesk created for these tests only. It is:
http://pythonfreshdesk.freshdesk.com/
"""

DOMAIN = 'pythonfreshdesk.freshdesk.com'
API_KEY = 'MX4CEAw4FogInimEdRW2'


class MockedAPI(API):
    def __init__(self, *args):
        self.resolver = {
            'get': {
                re.compile(r'helpdesk/tickets/filter/all_tickets\?format=json&page=1'): self.read_test_file(
                    'all_tickets.json'),
                re.compile(r'helpdesk/tickets/filter/new_my_open\?format=json&page=1'): self.read_test_file(
                    'all_tickets.json'),
                re.compile(r'helpdesk/tickets/filter/spam\?format=json&page=1'): [],
                re.compile(r'helpdesk/tickets/filter/deleted\?format=json&page=1'): [],
                re.compile(r'helpdesk/tickets/1/time_sheets.json'): self.read_test_file('timeentries_ticket_1.json'),
                re.compile(r'helpdesk/tickets/1.json'): self.read_test_file('ticket_1.json'),
                re.compile(r'.*&page=2'): [],
                re.compile(r'contacts.json'): self.read_test_file('contacts.json'),
                re.compile(r'contacts/1.json'): self.read_test_file('contact.json'),
                re.compile(r'contacts/1.json'): self.read_test_file('contact.json'),
                re.compile(r'agents.json\?$'): self.read_test_file('agents.json'),
                re.compile(r'agents/1.json$'): self.read_test_file('agent_1.json'),
                re.compile(r'customers/1.json'): self.read_test_file('customer.json'),
                re.compile(r'helpdesk/time_sheets.json'): self.read_test_file('timeentries_ticket_1.json'),
                re.compile(r'helpdesk/time_sheets.json\?agent_id='): self.read_test_file('timeentries_ticket_1.json'),
                re.compile(r'helpdesk/time_sheets.json'): self.read_test_file('timeentries_ticket_1.json'),
            },
            'post': {
                re.compile(r'helpdesk/tickets.json'): self.read_test_file('ticket_1.json'),
                re.compile(r'contacts.json'): self.read_test_file('contact.json'),
                re.compile(r'agents/1.json$'): self.read_test_file('agent_1.json'),
            },
            'put': {
                re.compile(r'contacts/1/make_agent.json'): self.read_test_file('agent_1.json'),
                re.compile(r'agents/1.json$'): self.read_test_file('agent_1_updated.json'),
            },
            'delete': {
                re.compile(r'helpdesk/tickets/1.json'): None,
                re.compile(r'contacts/1.json'): None,
                re.compile(r'agents/1.json$'): None,
            }
        }

        super(MockedAPI, self).__init__(*args)

    def read_test_file(self, filename):
        path = os.path.join(os.path.dirname(__file__), 'sample_json_data', filename)
        return json.loads(open(path, 'r').read())

    def _get(self, url, *args, **kwargs):
        for pattern, j in self.resolver['get'].items():
            if pattern.match(url):
                return j

        # No match found, raise 404
        from requests.exceptions import HTTPError
        raise HTTPError('404: mocked_api_get() has no pattern for \'{}\''.format(url))

    def _post(self, url, *args, **kwargs):
        for pattern, data in self.resolver['post'].items():
            if pattern.match(url):
                return data

        # No match found, raise 404
        from requests.exceptions import HTTPError
        raise HTTPError('404: mocked_api_post() has no pattern for \'{}\''.format(url))

    def _put(self, url, *args, **kwargs):
        for pattern, data in self.resolver['put'].items():
            if pattern.match(url):
                return data

        # No match found, raise 404
        from requests.exceptions import HTTPError
        raise HTTPError('404: mocked_api_put() has no pattern for \'{}\''.format(url))

    def _delete(self, url, *args, **kwargs):
        for pattern, data in self.resolver['delete'].items():
            if pattern.match(url):
                return data

        # No match found, raise 404
        from requests.exceptions import HTTPError
        raise HTTPError('404: mocked_api_delete() has no pattern for \'{}\''.format(url))


class TestAPIClass(TestCase):
    def test_api_prefix(self):
        api = API('test_domain', 'test_key')
        self.assertEqual(api._api_prefix, 'https://test_domain/')
        api = API('test_domain/', 'test_key')
        self.assertEqual(api._api_prefix, 'https://test_domain/')

    @responses.activate
    def test_403_error(self):
        responses.add(responses.GET,
                      'https://{}/helpdesk/tickets/1.json'.format(DOMAIN),
                      status=403)

        api = API(DOMAIN, 'invalid_api_key')
        from requests.exceptions import HTTPError
        with self.assertRaises(HTTPError):
            api.tickets.get_ticket(1)

    @responses.activate
    def test_404_error(self):
        DOMAIN_404 = 'google.com'
        responses.add(responses.GET,
                      'https://{}/helpdesk/tickets/1.json'.format(DOMAIN_404),
                      status=404)

        api = API(DOMAIN_404, 'invalid_api_key')
        from requests.exceptions import HTTPError
        with self.assertRaises(HTTPError):
            api.tickets.get_ticket(1)


class TestTicket(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = MockedAPI(DOMAIN, API_KEY)
        cls.ticket = cls.api.tickets.get_ticket(1)
        cls.ticket_json = json.loads(open(os.path.join(os.path.dirname(__file__),
                                                       'sample_json_data',
                                                       'ticket_1.json')).read())

    def test_str(self):
        self.assertEqual(str(self.ticket), 'This is a sample ticket')

    def test_repr(self):
        self.assertEqual(repr(self.ticket), '<Ticket \'This is a sample ticket\'>')

    def test_create_ticket(self):
        ticket = self.api.tickets.create_ticket('This is a sample ticket',
                                                description='This is a sample ticket, feel free to delete it.',
                                                email='test@example.com',
                                                priority=1, status=2,
                                                tags=['foo', 'bar'],
                                                cc_emails=['test2@example.com'])
        self.assertIsInstance(ticket, Ticket)
        self.assertEqual(ticket.subject, 'This is a sample ticket')
        self.assertEqual(ticket.description, 'This is a sample ticket, feel free to delete it.')
        self.assertEqual(ticket.priority, 'low')
        self.assertEqual(ticket.status, 'open')
        self.assertEqual(ticket.cc_email['cc_emails'], ['test2@example.com'])
        self.assertIn('foo', ticket.tags)
        self.assertIn('bar', ticket.tags)
            
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

    def test_none_filter_name(self):
        tickets = self.api.tickets.list_tickets(filter_name=None)
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


class TestContact(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = MockedAPI(DOMAIN, API_KEY)
        cls.contact = cls.api.contacts.get_contact(1)

    def test_get_contact(self):
        self.assertIsInstance(self.contact, Contact)
        self.assertEqual(self.contact.name, 'Rachel')
        self.assertEqual(self.contact.email, 'rachel@freshdesk.com')
        self.assertEqual(self.contact.helpdesk_agent, False)
        self.assertEqual(self.contact.customer_id, 1)

    def test_list_contacts(self):
        contacts = self.api.contacts.list_contacts()
        self.assertIsInstance(contacts, list)
        self.assertEquals(len(contacts), 2)
        self.assertIsInstance(contacts[0], Contact)
        self.assertEquals(contacts[0].id, self.contact.id)
        self.assertEquals(contacts[0].email, self.contact.email)
        self.assertEquals(contacts[0].name, self.contact.name)

    def test_create_contact(self):
        contact_data = {
            'name': 'Rachel',
            'email': 'rachel@freshdesk.com'
        }
        contact = self.api.contacts.create_contact(contact_data)
        self.assertIsInstance(contact, Contact)
        self.assertEquals(contact.id, self.contact.id)
        self.assertEquals(contact.email, self.contact.email)
        self.assertEquals(contact.name, self.contact.name)

    def test_make_agent(self):
        agent = self.api.contacts.make_agent(self.contact.id)
        self.assertIsInstance(agent, Agent)
        self.assertEquals(agent.available, True)
        self.assertEquals(agent.occasional, False)
        self.assertEquals(agent.id, 1)
        self.assertEquals(agent.user_id, self.contact.id)
        self.assertEquals(agent.user['email'], self.contact.email)
        self.assertEquals(agent.user['name'], self.contact.name)

    def test_delete_contact(self):
        self.assertEquals(self.api.contacts.delete_contact(1), None)

    def test_contact_datetime(self):
        self.assertIsInstance(self.contact.created_at, datetime.datetime)
        self.assertIsInstance(self.contact.updated_at, datetime.datetime)

    def test_contact_str(self):
        self.assertEqual(str(self.contact), 'Rachel')

    def test_contact_repr(self):
        self.assertEqual(repr(self.contact), '<Contact \'Rachel\'>')


class TestCustomer(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = MockedAPI(DOMAIN, API_KEY)
        cls.customer = cls.api.customers.get_customer(1)
        cls.contact = cls.api.contacts.get_contact(1)

    def test_customer(self):
        self.assertIsInstance(self.customer, Customer)
        self.assertEqual(self.customer.name, 'ACME Corp.')
        self.assertEqual(self.customer.domains, 'acme.com')
        self.assertEqual(self.customer.cf_custom_key, 'custom_value')

    def test_contact_datetime(self):
        self.assertIsInstance(self.customer.created_at, datetime.datetime)
        self.assertIsInstance(self.customer.updated_at, datetime.datetime)

    def test_contact_str(self):
        self.assertEqual(str(self.customer), 'ACME Corp.')

    def test_contact_repr(self):
        self.assertEqual(repr(self.customer), '<Customer \'ACME Corp.\'>')

    def test_get_customer_from_contact(self):
        self.customer = self.api.customers.get_customer_from_contact(self.contact)
        self.test_customer()


class TestTimesheets(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = MockedAPI(DOMAIN, API_KEY)
        cls.timesheet = cls.api.timesheets.get_timesheet_by_ticket(1)

    def test_timesheet(self):
        self.assertIsInstance(self.timesheet, type([]))
        self.assertEqual(len(self.timesheet), 3)
        self.assertIsInstance(self.timesheet[1], TimeEntry)
        self.assertEqual(self.timesheet[1].id, 6000041896)
        self.assertEqual(self.timesheet[1].note, "Foo")
        self.assertEqual(self.timesheet[1].timespent, "0.33")

    def test_timesheet_str(self):
        self.assertEqual(str(self.timesheet[1]), "6000041896")

    def test_timesheet_repr(self):
        self.assertEqual(repr(self.timesheet[1]), '<Timesheet Entry 6000041896>')

    def test_get_all_timesheets(self):
        self.timesheet = self.api.timesheets.get_all_timesheets()
        self.test_timesheet()
        self.timesheet = self.api.timesheets.get_all_timesheets(filter_name="agent_id", filter_value="5004272350")
        self.test_timesheet()


class TestAgent(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = MockedAPI(DOMAIN, API_KEY)
        cls.agent = cls.api.agents.get_agent(1)
        cls.agent_json = json.loads(open(os.path.join(os.path.dirname(__file__),
                                                      'sample_json_data',
                                                      'agent_1.json')).read())

    def test_str(self):
        self.assertEqual(str(self.agent), 'Rachel')

    def test_repr(self):
        self.assertEqual(repr(self.agent), '<Agent #1 \'Rachel\'>')

    def test_list_agents(self):
        agents = self.api.agents.list_agents()
        self.assertIsInstance(agents, list)
        self.assertEqual(len(agents), 2)
        self.assertEqual(agents[0].id, self.agent.id)

    def test_get_agent(self):
        self.assertIsInstance(self.agent, Agent)
        self.assertEqual(self.agent.id, 1)
        self.assertEqual(self.agent.user['name'], 'Rachel')
        self.assertEqual(self.agent.user['email'], 'rachel@freshdesk.com')
        self.assertEqual(self.agent.user['mobile'], 1234)
        self.assertEqual(self.agent.user['phone'], 5678)
        self.assertEqual(self.agent.occasional, False)

    def test_update_agent(self):
        values = {
            'occasional': True,
            'contact': {
                'name': 'Updated Name'
            }
        }
        agent = self.api.agents.update_agent(1, **values)

        self.assertEqual(agent.occasional, True)
        self.assertEqual(agent.user['name'], 'Updated Name')

    def test_delete_agent(self):
        self.assertEquals(self.api.agents.delete_agent(1), None)

    def test_agent_name(self):
        self.assertEqual(self.agent.user['name'], 'Rachel')

    def test_agent_mobile(self):
        self.assertEqual(self.agent.user['mobile'], 1234)

    def test_agent_state(self):
        self.assertEqual(self.agent.available, True)
        self.assertEqual(self.agent.occasional, False)

    def test_agent_datetime(self):
        self.assertIsInstance(self.agent.created_at, datetime.datetime)
        self.assertIsInstance(self.agent.updated_at, datetime.datetime)
