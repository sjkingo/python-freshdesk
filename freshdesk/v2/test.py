import datetime
import json
import os.path
import re

import pytest
import responses

from freshdesk.v2.api import API
from freshdesk.v2.errors import (
    FreshdeskAccessDenied, FreshdeskBadRequest, FreshdeskError, FreshdeskNotFound, FreshdeskRateLimited,
    FreshdeskServerError,
)
from freshdesk.v2.models import Agent, Comment, Contact, Customer, Group, Role, Ticket

"""
Test suite for python-freshdesk.

We test against a dummy helpdesk created for these tests only. It is:
https://pythonfreshdesk.freshdesk.com/
"""

DOMAIN = 'pythonfreshdesk.freshdesk.com'
API_KEY = 'MX4CEAw4FogInimEdRW2'


class MockedAPI(API):
    def __init__(self, *args):
        self.resolver = {
            'get': {
                re.compile(r'tickets\?filter=new_and_my_open&page=1&per_page=100'): self.read_test_file('all_tickets.json'),
                re.compile(r'tickets\?filter=deleted&page=1&per_page=100'): self.read_test_file('all_tickets.json'),
                re.compile(r'tickets\?filter=spam&page=1&per_page=100'): self.read_test_file('all_tickets.json'),
                re.compile(r'tickets\?filter=watching&page=1&per_page=100'): self.read_test_file('all_tickets.json'),
                re.compile(r'tickets\?page=1&per_page=100'): self.read_test_file('all_tickets.json'),
                re.compile(r'tickets/1$'): self.read_test_file('ticket_1.json'),
                re.compile(r'tickets/1/conversations'): self.read_test_file('conversations.json'),
                re.compile(r'contacts\?page=1&per_page=100$'): self.read_test_file('contacts.json'),
                re.compile(r'contacts/1$'): self.read_test_file('contact.json'),
                re.compile(r'customers/1$'): self.read_test_file('customer.json'),
                re.compile(r'groups\?page=1&per_page=100$'): self.read_test_file('groups.json'),
                re.compile(r'groups/1$'): self.read_test_file('group_1.json'),
                re.compile(r'roles$'): self.read_test_file('roles.json'),
                re.compile(r'roles/1$'): self.read_test_file('role_1.json'),
                re.compile(r'agents\?email=abc@xyz.com&page=1&per_page=100'): self.read_test_file('agent_1.json'),
                re.compile(r'agents\?mobile=1234&page=1&per_page=100'): self.read_test_file('agent_1.json'),
                re.compile(r'agents\?phone=5678&page=1&per_page=100'): self.read_test_file('agent_1.json'),
                re.compile(r'agents\?state=fulltime&page=1&per_page=100'): self.read_test_file('agent_1.json'),
                re.compile(r'agents\?page=1&per_page=100'): self.read_test_file('agents.json'),
                re.compile(r'agents/1$'): self.read_test_file('agent_1.json'),
            },
            'post': {
                re.compile(r'tickets$'): self.read_test_file('ticket_1.json'),
                re.compile(r'tickets/outbound_email$'): self.read_test_file('outbound_email_1.json'),
                re.compile(r'tickets/1/notes$'): self.read_test_file('note_1.json'),
                re.compile(r'tickets/1/reply$'): self.read_test_file('reply_1.json'),
                re.compile(r'contacts$'): self.read_test_file('contact.json'),
            },
            'put': {
                re.compile(r'tickets/1$'): self.read_test_file('ticket_1_updated.json'),
                re.compile(r'contacts/1$'): self.read_test_file('contact_updated.json'),
                re.compile(r'contacts/1/restore$'): self.read_test_file('contact.json'),
                re.compile(r'contacts/1/make_agent$'): self.read_test_file('contact_1_agent.json'),
                re.compile(r'agents/1$'): self.read_test_file('agent_1_updated.json'),
            },
            'delete': {
                re.compile(r'tickets/1$'): None,
                re.compile(r'agents/1$'): None,
                re.compile(r'contacts/1$'): None,
                re.compile(r'contacts/1/hard_delete\?force=True$'): None,
            }
        }

        super(MockedAPI, self).__init__(*args)

    def read_test_file(self, filename):
        path = os.path.join(os.path.dirname(__file__), 'sample_json_data', filename)
        return json.loads(open(path, 'r').read())

    def _get(self, url, *args, **kwargs):
        for pattern, data in self.resolver['get'].items():
            if pattern.match(url):
                return data

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
    def test_custom_cname(self):
        with pytest.raises(AttributeError):
            API('custom_cname_domain', 'invalid_api_key')

    def test_api_prefix(self):
        api = API('test_domain.freshdesk.com', 'test_key')
        assert api._api_prefix == 'https://test_domain.freshdesk.com/api/v2/'
        api = API('test_domain.freshdesk.com/', 'test_key')
        assert api._api_prefix == 'https://test_domain.freshdesk.com/api/v2/'

    @responses.activate
    @pytest.mark.parametrize(
        ('status_code', 'exception'),
        [(400, FreshdeskBadRequest), (403, FreshdeskAccessDenied), (404, FreshdeskNotFound),
         (418, FreshdeskError), (429, FreshdeskRateLimited), (502, FreshdeskServerError)]
    )
    def test_errors(self, status_code, exception):
        responses.add(responses.GET,
                      'https://{}/api/v2/tickets/1'.format(DOMAIN),
                      status=status_code)

        api = API('pythonfreshdesk.freshdesk.com', 'test_key')
        with pytest.raises(exception):
            api.tickets.get_ticket(1)


class TestTicket:
    def setup(self):
        self.api = MockedAPI(DOMAIN, API_KEY)
        self.ticket = self.api.tickets.get_ticket(1)
        self.ticket_json = json.loads(open(os.path.join(os.path.dirname(__file__),
                                                       'sample_json_data',
                                                       'ticket_1.json')).read())
        self.outbound_email_json = json.loads(open(os.path.join(os.path.dirname(__file__),
                                                       'sample_json_data',
                                                       'outbound_email_1.json')).read())

    def test_str(self):
        assert str(self.ticket) == 'This is a sample ticket'

    def test_repr(self):
        assert repr(self.ticket) == '<Ticket \'This is a sample ticket\' #1>'

    def test_get_ticket(self):
        assert isinstance(self.ticket, Ticket)
        assert self.ticket.id == 1
        assert self.ticket.subject == 'This is a sample ticket'
        assert self.ticket.description_text, 'This is a sample ticket == feel free to delete it.'
        assert self.ticket.cc_emails == ['test2@example.com']
        assert 'foo' in self.ticket.tags
        assert 'bar' in self.ticket.tags

    def test_create_ticket(self):
        attachment_path = os.path.join(os.path.dirname(__file__), 'sample_json_data', 'attachment.txt')
        ticket = self.api.tickets.create_ticket('This is a sample ticket',
                                                description='This is a sample ticket, feel free to delete it.',
                                                email='test@example.com',
                                                priority=1, status=2,
                                                tags=['foo', 'bar'],
                                                cc_emails=['test2@example.com'],
                                                attachments=(attachment_path,))
        assert isinstance(ticket, Ticket)
        assert ticket.subject == 'This is a sample ticket'
        assert ticket.description_text, 'This is a sample ticket == feel free to delete it.'
        assert ticket.priority == 'low'
        assert ticket.status == 'open'
        assert ticket.cc_emails == ['test2@example.com']
        assert 'foo' in ticket.tags
        assert 'bar' in ticket.tags

    def test_create_outbound_email(self):
        j = self.outbound_email_json.copy()
        email = 'test@example.com'
        subject = 'This is a sample outbound email'
        description = 'This is a sample outbound email, feel free to delete it.'
        email_config_id = 5000054536
        values = {
            'status': 5,
            'priority': 1,
            'tags': ['foo', 'bar'],
            'cc_emails': ['test2@example.com']
        }

        email = self.api.tickets.create_outbound_email(
                subject,
                description,
                email,
                email_config_id,
                **values
        )

        assert email.description_text == j['description_text']
        assert email._priority == j['priority']
        assert email._status == j['status']
        assert email.cc_emails == j['cc_emails']
        assert 'foo' in email.tags
        assert 'bar' in email.tags

    def test_update_ticket(self):
        j = self.ticket_json.copy()
        values = {
            'subject': 'Test subject update',
            'priority': 3,
            'status': 4,
            'tags': ['hello', 'world']
        }
        j.update(values)

        ticket = self.api.tickets.update_ticket(j['id'], **values)
        assert ticket.subject == 'Test subject update'
        assert ticket.status == 'resolved'
        assert ticket.priority == 'high'
        assert 'hello' in ticket.tags
        assert 'world' in ticket.tags

    def test_delete_ticket(self):
        assert self.api.tickets.delete_ticket(1) is None

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

    def test_new_and_my_open_tickets(self):
        tickets = self.api.tickets.list_new_and_my_open_tickets()
        assert isinstance(tickets, list)
        assert len(tickets) == 1
        assert tickets[0].id == self.ticket.id

    def test_deleted_tickets(self):
        tickets = self.api.tickets.list_deleted_tickets()
        assert isinstance(tickets, list)
        assert len(tickets) == 1

    def test_watched_tickets(self):
        tickets = self.api.tickets.list_watched_tickets()
        assert isinstance(tickets, list)
        assert len(tickets) == 1
        assert tickets[0].id == self.ticket.id

    def test_spam_tickets(self):
        tickets = self.api.tickets.list_tickets(filter_name='spam')
        assert isinstance(tickets, list)
        assert len(tickets) == 1

    def test_default_filter_name(self):
        tickets = self.api.tickets.list_tickets()
        assert isinstance(tickets, list)
        assert len(tickets) == 1
        assert tickets[0].id == self.ticket.id

    def test_none_filter_name(self):
        tickets = self.api.tickets.list_tickets(filter_name=None)
        assert isinstance(tickets, list)
        assert len(tickets) == 1
        assert tickets[0].id == self.ticket.id


class TestComment:
    def setup(self):
        self.api = MockedAPI(DOMAIN, API_KEY)
        self.comments = self.api.comments.list_comments(1)
        self.comments_json = json.loads(open(os.path.join(
            os.path.dirname(__file__),
            'sample_json_data',
            'conversations.json')).read())

    def test_comments_list(self):
        assert isinstance(self.comments, list)
        assert len(self.comments) == 2
        assert isinstance(self.comments[0], Comment)

    def test_comment_str(self):
        assert str(self.comments[0]) == 'This is a private note'

    def test_comment_repr(self):
        assert repr(self.comments[0]) == '<Comment for Ticket #1>'

    def test_create_note(self):
        comment = self.api.comments.create_note(1, 'This is a private note')
        assert isinstance(comment, Comment)
        assert comment.body_text == 'This is a private note'
        assert comment.source == 'note'

    def test_create_reply(self):
        comment = self.api.comments.create_reply(1, 'This is a reply')
        assert isinstance(comment, Comment)
        assert comment.body_text == 'This is a reply'
        assert comment.source == 'reply'


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

    def test_list_contact(self):
        contacts = self.api.contacts.list_contacts()
        assert isinstance(contacts, list)
        assert isinstance(contacts[0], Contact)
        assert len(contacts) == 2
        assert contacts[0].__dict__ == self.contact.__dict__

    def test_create_contact(self):
        contact_data = {
            'name': 'Rachel',
            'email': 'rachel@freshdesk.com'
        }
        contact = self.api.contacts.create_contact(contact_data)
        assert isinstance(contact, Contact)
        assert contact.email == self.contact.email
        assert contact.name == self.contact.name

    def test_update_contact(self):
        contact_data = {
            'name': 'New Name'
        }
        contact = self.api.contacts.update_contact(1, **contact_data)
        assert isinstance(contact, Contact)
        assert contact.name == 'New Name'

    def test_soft_delete_contact(self):
        assert self.api.contacts.soft_delete_contact(1) is None

    def test_permanently_delete_contact(self):
        assert self.api.contacts.permanently_delete_contact(1) is None

    def test_restore_contact(self):
        self.api.contacts.restore_contact(1)
        contact = self.api.contacts.get_contact(1)
        assert isinstance(contact, Contact)
        assert contact.deleted is False

    def test_make_agent(self):
        agent = self.api.contacts.make_agent(self.contact.id)
        assert isinstance(agent, Agent)
        assert agent.available is True
        assert agent.occasional is False
        assert agent.contact['email'] == self.contact.email
        assert agent.contact['name'] == self.contact.name

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
        self.customer = self.api.customers.get_customer('1')
        self.contact = self.api.contacts.get_contact(1)

    def test_customer(self):
        assert isinstance(self.customer, Customer)
        assert self.customer.name == 'ACME Corp.'
        assert self.customer.domains == 'acme.com'
        assert self.customer.cf_custom_key == 'custom_value'

    def test_customer_datetime(self):
        assert isinstance(self.customer.created_at, datetime.datetime)
        assert isinstance(self.customer.updated_at, datetime.datetime)

    def test_customer_str(self):
        assert str(self.customer) == 'ACME Corp.'

    def test_customer_repr(self):
        assert repr(self.customer) == '<Customer \'ACME Corp.\'>'

    def test_get_customer_from_contact(self):
        self.customer = self.api.customers.get_customer_from_contact(self.contact)
        self.test_customer()


class TestGroup:
    def setup(self):
        self.api = MockedAPI(DOMAIN, API_KEY)
        self.group = self.api.groups.get_group(1)

    def test_list_groups(self):
        groups = self.api.groups.list_groups()
        assert isinstance(groups, list)
        assert len(groups) == 2
        assert groups[0].id == self.group.id

    def test_group(self):
        assert isinstance(self.group, Group)
        assert self.group.name == 'Entertainers'
        assert self.group.description == 'Singers dancers and stand up comedians'

    def test_group_datetime(self):
        assert isinstance(self.group.created_at, datetime.datetime)
        assert isinstance(self.group.updated_at, datetime.datetime)

    def test_group_str(self):
        assert str(self.group) == 'Entertainers'

    def test_group_repr(self):
        assert repr(self.group) == '<Group \'Entertainers\'>'


class TestRole:
    def setup(self):
        self.api = MockedAPI(DOMAIN, API_KEY)
        self.role = self.api.roles.get_role(1)

    def test_list_roles(self):
        roles = self.api.roles.list_roles()
        assert isinstance(roles, list)
        assert len(roles) == 2
        assert roles[0].id == self.role.id

    def test_role(self):
        assert isinstance(self.role, Role)
        assert self.role.name == 'Agent'
        assert self.role.description, 'Can log, view, reply == update and resolve tickets and manage contacts.'

    def test_group_datetime(self):
        assert isinstance(self.role.created_at, datetime.datetime)
        assert isinstance(self.role.updated_at, datetime.datetime)

    def test_group_repr(self):
        assert repr(self.role) == '<Role \'Agent\'>'


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

    def test_get_agent(self):
        assert isinstance(self.agent, Agent)
        assert self.agent.id == 1
        assert self.agent.contact['name'] == 'Rachel'
        assert self.agent.contact['email'] == 'rachel@freshdesk.com'
        assert self.agent.contact['mobile'] == 1234
        assert self.agent.contact['phone'] == 5678
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
        assert agent.contact['name'] == 'Updated Name'
    
    def test_delete_agent(self):
        assert self.api.agents.delete_agent(1) is None

    def test_agent_name(self):
        assert self.agent.contact['name'] == 'Rachel'
        
    def test_agent_mobile(self):
        assert self.agent.contact['mobile'] == 1234
    
    def test_agent_state(self):
        assert self.agent.available is True
        assert self.agent.occasional is False

    def test_agent_datetime(self):
        assert isinstance(self.agent.created_at, datetime.datetime)
        assert isinstance(self.agent.updated_at, datetime.datetime)

    def test_none_filter_name(self):
        agents = self.api.agents.list_agents()
        assert isinstance(agents, list)
        assert len(agents) == 2
        assert agents[0].id == self.agent.id
