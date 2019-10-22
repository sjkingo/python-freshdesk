import datetime
import json
import os.path
import re

import pytest
import responses

from freshdesk.v1.api import API
from freshdesk.v1.models import Agent, Comment, Contact, Customer, Ticket, TimeEntry

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


class TestAPIClass:
    def test_api_prefix(self):
        api = API('test_domain', 'test_key')
        assert api._api_prefix == 'https://test_domain/'
        api = API('test_domain/', 'test_key')
        assert api._api_prefix == 'https://test_domain/'

    @responses.activate
    def test_403_error(self):
        responses.add(responses.GET,
                      'https://{}/helpdesk/tickets/1.json'.format(DOMAIN),
                      status=403)

        api = API(DOMAIN, 'invalid_api_key')
        from requests.exceptions import HTTPError
        with pytest.raises(HTTPError):
            api.tickets.get_ticket(1)

    @responses.activate
    def test_404_error(self):
        DOMAIN_404 = 'google.com'
        responses.add(responses.GET,
                      'https://{}/helpdesk/tickets/1.json'.format(DOMAIN_404),
                      status=404)

        api = API(DOMAIN_404, 'invalid_api_key')
        from requests.exceptions import HTTPError
        with pytest.raises(HTTPError):
            api.tickets.get_ticket(1)


class TestTicket:
    def setup(self):
        self.api = MockedAPI(DOMAIN, API_KEY)
        self.ticket = self.api.tickets.get_ticket(1)
        self.ticket_json = json.loads(open(os.path.join(os.path.dirname(__file__),
                                                       'sample_json_data',
                                                       'ticket_1.json')).read())

    def test_str(self):
        assert str(self.ticket) == 'This is a sample ticket'

    def test_repr(self):
        assert repr(self.ticket) == '<Ticket \'This is a sample ticket\'>'

    def test_create_ticket(self):
        ticket = self.api.tickets.create_ticket('This is a sample ticket',
                                                description='This is a sample ticket, feel free to delete it.',
                                                email='test@example.com',
                                                priority=1, status=2,
                                                tags=['foo', 'bar'],
                                                cc_emails=['test2@example.com'])
        assert isinstance(ticket, Ticket)
        assert ticket.subject == 'This is a sample ticket'
        assert ticket.description, 'This is a sample ticket == feel free to delete it.'
        assert ticket.priority == 'low'
        assert ticket.status == 'open'
        assert ticket.cc_email['cc_emails'] == ['test2@example.com']
        assert 'foo' in ticket.tags
        assert 'bar' in ticket.tags
            
    def test_get_ticket(self):
        assert isinstance(self.ticket, Ticket)
        assert self.ticket.display_id == 1
        assert self.ticket.subject == 'This is a sample ticket'
        assert self.ticket.description, 'This is a sample ticket == feel free to delete it.'

    def test_ticket_priority(self):
        assert self.ticket._priority == 1
        assert self.ticket.priority == 'low'

    def test_ticket_status(self):
        assert self.ticket._status == 2
        assert self.ticket.status == 'open'

    def test_ticket_source(self):
        assert self.ticket._source == 2
        assert self.ticket.source == 'portal'

    def test_ticket_datetime(self):
        assert isinstance(self.ticket.created_at, datetime.datetime)
        assert isinstance(self.ticket.updated_at, datetime.datetime)

    def test_all_tickets(self):
        tickets = self.api.tickets.list_all_tickets()
        assert isinstance(tickets, list)
        assert len(tickets) == 1
        assert tickets[0].display_id == self.ticket.display_id

    def test_open_tickets(self):
        tickets = self.api.tickets.list_open_tickets()
        assert isinstance(tickets, list)
        assert len(tickets) == 1
        assert tickets[0].display_id == self.ticket.display_id

    def test_deleted_tickets(self):
        tickets = self.api.tickets.list_deleted_tickets()
        assert isinstance(tickets, list)
        assert len(tickets) == 0

    def test_spam_tickets(self):
        tickets = self.api.tickets.list_tickets(filter_name='spam')
        assert isinstance(tickets, list)
        assert len(tickets) == 0

    def test_default_filter_name(self):
        tickets = self.api.tickets.list_tickets()
        assert isinstance(tickets, list)
        assert len(tickets) == 1
        assert tickets[0].display_id == self.ticket.display_id

    def test_none_filter_name(self):
        tickets = self.api.tickets.list_tickets(filter_name=None)
        assert isinstance(tickets, list)
        assert len(tickets) == 1
        assert tickets[0].display_id == self.ticket.display_id


class TestComment:
    def setup(self):
        self.api = MockedAPI(DOMAIN, API_KEY)
        self.ticket = self.api.tickets.get_ticket(1)

    def test_comments_list(self):
        assert isinstance(self.ticket.comments, list)
        assert len(self.ticket.comments) == 1
        assert isinstance(self.ticket.comments[0], Comment)

    def test_comment_str(self):
        assert str(self.ticket.comments[0]) == 'This is a reply.'

    def test_comment_repr(self):
        assert repr(self.ticket.comments[0]) == '<Comment for <Ticket \'This is a sample ticket\'>>'


class TestContact:
    def setup(self):
        self.api = MockedAPI(DOMAIN, API_KEY)
        self.contact = self.api.contacts.get_contact(1)

    def test_get_contact(self):
        assert isinstance(self.contact, Contact)
        assert self.contact.name == 'Rachel'
        assert self.contact.email == 'rachel@freshdesk.com'
        assert self.contact.helpdesk_agent is False
        assert self.contact.customer_id == 1

    def test_list_contacts(self):
        contacts = self.api.contacts.list_contacts()
        assert isinstance(contacts, list)
        assert len(contacts) == 2
        assert isinstance(contacts[0], Contact)
        assert contacts[0].id == self.contact.id
        assert contacts[0].email == self.contact.email
        assert contacts[0].name == self.contact.name

    def test_create_contact(self):
        contact_data = {
            'name': 'Rachel',
            'email': 'rachel@freshdesk.com'
        }
        contact = self.api.contacts.create_contact(contact_data)
        assert isinstance(contact, Contact)
        assert contact.id == self.contact.id
        assert contact.email == self.contact.email
        assert contact.name == self.contact.name

    def test_make_agent(self):
        agent = self.api.contacts.make_agent(self.contact.id)
        assert isinstance(agent, Agent)
        assert agent.available is True
        assert agent.occasional is False
        assert agent.id == 1
        assert agent.user_id == self.contact.id
        assert agent.user['email'] == self.contact.email
        assert agent.user['name'] == self.contact.name

    def test_delete_contact(self):
        assert self.api.contacts.delete_contact(1) is None

    def test_contact_datetime(self):
        assert isinstance(self.contact.created_at, datetime.datetime)
        assert isinstance(self.contact.updated_at, datetime.datetime)

    def test_contact_str(self):
        assert str(self.contact) == 'Rachel'

    def test_contact_repr(self):
        assert repr(self.contact) == '<Contact \'Rachel\'>'


class TestCustomer:
    def setup(self):
        self.api = MockedAPI(DOMAIN, API_KEY)
        self.customer = self.api.customers.get_customer(1)
        self.contact = self.api.contacts.get_contact(1)

    def test_customer(self):
        assert isinstance(self.customer, Customer)
        assert self.customer.name == 'ACME Corp.'
        assert self.customer.domains == 'acme.com'
        assert self.customer.cf_custom_key == 'custom_value'

    def test_contact_datetime(self):
        assert isinstance(self.customer.created_at, datetime.datetime)
        assert isinstance(self.customer.updated_at, datetime.datetime)

    def test_contact_str(self):
        assert str(self.customer) == 'ACME Corp.'

    def test_contact_repr(self):
        assert repr(self.customer) == '<Customer \'ACME Corp.\'>'

    def test_get_customer_from_contact(self):
        self.customer = self.api.customers.get_customer_from_contact(self.contact)
        self.test_customer()


class TestTimesheets:
    def setup(self):
        self.api = MockedAPI(DOMAIN, API_KEY)
        self.timesheet = self.api.timesheets.get_timesheet_by_ticket(1)

    def test_timesheet(self):
        assert isinstance(self.timesheet, type([]))
        assert len(self.timesheet) == 3
        assert isinstance(self.timesheet[1], TimeEntry)
        assert self.timesheet[1].id == 6000041896
        assert self.timesheet[1].note == "Foo"
        assert self.timesheet[1].timespent == "0.33"

    def test_timesheet_str(self):
        assert str(self.timesheet[1]) == "6000041896"

    def test_timesheet_repr(self):
        assert repr(self.timesheet[1]) == '<Timesheet Entry 6000041896>'

    def test_get_all_timesheets(self):
        self.timesheet = self.api.timesheets.get_all_timesheets()
        self.test_timesheet()
        self.timesheet = self.api.timesheets.get_all_timesheets(filter_name="agent_id", filter_value="5004272350")
        self.test_timesheet()


class TestAgent:
    def setup(self):
        self.api = MockedAPI(DOMAIN, API_KEY)
        self.agent = self.api.agents.get_agent(1)
        self.agent_json = json.loads(open(os.path.join(os.path.dirname(__file__),
                                                      'sample_json_data',
                                                      'agent_1.json')).read())

    def test_str(self):
        assert str(self.agent) == 'Rachel'

    def test_repr(self):
        assert repr(self.agent) == '<Agent #1 \'Rachel\'>'

    def test_list_agents(self):
        agents = self.api.agents.list_agents()
        assert isinstance(agents, list)
        assert len(agents) == 2
        assert agents[0].id == self.agent.id

    def test_get_agent(self):
        assert isinstance(self.agent, Agent)
        assert self.agent.id == 1
        assert self.agent.user['name'] == 'Rachel'
        assert self.agent.user['email'] == 'rachel@freshdesk.com'
        assert self.agent.user['mobile'] == 1234
        assert self.agent.user['phone'] == 5678
        assert self.agent.occasional is False

    def test_update_agent(self):
        values = {
            'occasional': True,
            'contact': {
                'name': 'Updated Name'
            }
        }
        agent = self.api.agents.update_agent(1, **values)

        assert agent.occasional is True
        assert agent.user['name'] == 'Updated Name'

    def test_delete_agent(self):
        assert self.api.agents.delete_agent(1) is None

    def test_agent_name(self):
        assert self.agent.user['name'] == 'Rachel'

    def test_agent_mobile(self):
        assert self.agent.user['mobile'] == 1234

    def test_agent_state(self):
        assert self.agent.available is True
        assert self.agent.occasional is False

    def test_agent_datetime(self):
        assert isinstance(self.agent.created_at, datetime.datetime)
        assert isinstance(self.agent.updated_at, datetime.datetime)
