import datetime
import json
import re
import os.path

import responses
from unittest import TestCase

from freshdesk.v2.api import API
from freshdesk.v2.models import Ticket, Comment, Contact, Customer, Group, Agent, Role

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


class TestAPIClass(TestCase):

    def test_custom_cname(self):
        with self.assertRaises(AttributeError):
            API('custom_cname_domain', 'invalid_api_key')

    def test_api_prefix(self):
        api = API('test_domain.freshdesk.com', 'test_key')
        self.assertEqual(api._api_prefix,
                         'https://test_domain.freshdesk.com/api/v2/')
        api = API('test_domain.freshdesk.com/', 'test_key')
        self.assertEqual(api._api_prefix,
                         'https://test_domain.freshdesk.com/api/v2/')

    @responses.activate
    def test_403_error(self):
        responses.add(responses.GET,
                      'https://{}/api/v2/tickets/1'.format(DOMAIN),
                      status=403)

        api = API('pythonfreshdesk.freshdesk.com', 'invalid_api_key')
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
        cls.outbound_email_json = json.loads(open(os.path.join(os.path.dirname(__file__),
                                                       'sample_json_data',
                                                       'outbound_email_1.json')).read())

    def test_str(self):
        self.assertEqual(str(self.ticket), 'This is a sample ticket')

    def test_repr(self):
        self.assertEqual(repr(self.ticket), '<Ticket \'This is a sample ticket\' #1>')

    def test_get_ticket(self):
        self.assertIsInstance(self.ticket, Ticket)
        self.assertEqual(self.ticket.id, 1)
        self.assertEqual(self.ticket.subject, 'This is a sample ticket')
        self.assertEqual(self.ticket.description_text, 'This is a sample ticket, feel free to delete it.')
        self.assertEqual(self.ticket.cc_emails, ['test2@example.com'])
        self.assertIn('foo', self.ticket.tags)
        self.assertIn('bar', self.ticket.tags)

    def test_create_ticket(self):
        attachment_path = os.path.join(os.path.dirname(__file__), 'sample_json_data', 'attachment.txt')
        ticket = self.api.tickets.create_ticket('This is a sample ticket',
                                                description='This is a sample ticket, feel free to delete it.',
                                                email='test@example.com',
                                                priority=1, status=2,
                                                tags=['foo', 'bar'],
                                                cc_emails=['test2@example.com'],
                                                attachments=(attachment_path,))
        self.assertIsInstance(ticket, Ticket)
        self.assertEqual(ticket.subject, 'This is a sample ticket')
        self.assertEqual(ticket.description_text, 'This is a sample ticket, feel free to delete it.')
        self.assertEqual(ticket.priority, 'low')
        self.assertEqual(ticket.status, 'open')
        self.assertEqual(ticket.cc_emails, ['test2@example.com'])
        self.assertIn('foo', ticket.tags)
        self.assertIn('bar', ticket.tags)

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

        self.assertEqual(email.description_text, j['description_text'])
        self.assertEqual(email._priority, j['priority'])
        self.assertEqual(email._status, j['status'])
        self.assertEqual(email.cc_emails, j['cc_emails'])
        self.assertIn('foo', email.tags)
        self.assertIn('bar', email.tags)

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
        self.assertEqual(ticket.subject, 'Test subject update')
        self.assertEqual(ticket.status, 'resolved')
        self.assertEqual(ticket.priority, 'high')
        self.assertIn('hello', ticket.tags)
        self.assertIn('world', ticket.tags)

    def test_delete_ticket(self):
        self.assertEquals(self.api.tickets.delete_ticket(1), None)

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

    def test_new_and_my_open_tickets(self):
        tickets = self.api.tickets.list_new_and_my_open_tickets()
        self.assertIsInstance(tickets, list)
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].id, self.ticket.id)

    def test_deleted_tickets(self):
        tickets = self.api.tickets.list_deleted_tickets()
        self.assertIsInstance(tickets, list)
        self.assertEqual(len(tickets), 1)

    def test_watched_tickets(self):
        tickets = self.api.tickets.list_watched_tickets()
        self.assertIsInstance(tickets, list)
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].id, self.ticket.id)

    def test_spam_tickets(self):
        tickets = self.api.tickets.list_tickets(filter_name='spam')
        self.assertIsInstance(tickets, list)
        self.assertEqual(len(tickets), 1)

    def test_default_filter_name(self):
        tickets = self.api.tickets.list_tickets()
        self.assertIsInstance(tickets, list)
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].id, self.ticket.id)

    def test_none_filter_name(self):
        tickets = self.api.tickets.list_tickets(filter_name=None)
        self.assertIsInstance(tickets, list)
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].id, self.ticket.id)


class TestComment(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = MockedAPI(DOMAIN, API_KEY)
        cls.comments = cls.api.comments.list_comments(1)
        cls.comments_json = json.loads(open(os.path.join(
            os.path.dirname(__file__),
            'sample_json_data',
            'conversations.json')).read())

    def test_comments_list(self):
        self.assertIsInstance(self.comments, list)
        self.assertEqual(len(self.comments), 2)
        self.assertIsInstance(self.comments[0], Comment)

    def test_comment_str(self):
        self.assertEqual(str(self.comments[0]), 'This is a private note')

    def test_comment_repr(self):
        self.assertEqual(repr(self.comments[0]), '<Comment for Ticket #1>')

    def test_create_note(self):
        comment = self.api.comments.create_note(1, 'This is a private note')
        self.assertIsInstance(comment, Comment)
        self.assertEqual(comment.body_text, 'This is a private note')
        self.assertEqual(comment.source, 'note')

    def test_create_reply(self):
        comment = self.api.comments.create_reply(1, 'This is a reply')
        self.assertIsInstance(comment, Comment)
        self.assertEqual(comment.body_text, 'This is a reply')
        self.assertEqual(comment.source, 'reply')


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

    def test_list_contact(self):
        contacts = self.api.contacts.list_contacts()
        self.assertIsInstance(contacts, list)
        self.assertIsInstance(contacts[0], Contact)
        self.assertEquals(len(contacts), 2)
        self.assertEquals(contacts[0].__dict__, self.contact.__dict__)

    def test_create_contact(self):
        contact_data = {
            'name': 'Rachel',
            'email': 'rachel@freshdesk.com'
        }
        contact = self.api.contacts.create_contact(contact_data)
        self.assertIsInstance(contact, Contact)
        self.assertEquals(contact.email, self.contact.email)
        self.assertEquals(contact.name, self.contact.name)

    def test_update_contact(self):
        contact_data = {
            'name': 'New Name'
        }
        contact = self.api.contacts.update_contact(1, **contact_data)
        self.assertIsInstance(contact, Contact)
        self.assertEquals(contact.name, 'New Name')

    def test_soft_delete_contact(self):
        self.assertEquals(self.api.contacts.soft_delete_contact(1), None)

    def test_permanently_delete_contact(self):
        self.assertEquals(self.api.contacts.permanently_delete_contact(1), None)

    def test_restore_contact(self):
        self.api.contacts.restore_contact(1)
        contact = self.api.contacts.get_contact(1)
        self.assertIsInstance(contact, Contact)
        self.assertEquals(contact.deleted, False)

    def test_make_agent(self):
        agent = self.api.contacts.make_agent(self.contact.id)
        self.assertIsInstance(agent, Agent)
        self.assertEquals(agent.available, True)
        self.assertEquals(agent.occasional, False)
        self.assertEquals(agent.contact['email'], self.contact.email)
        self.assertEquals(agent.contact['name'], self.contact.name)

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
        cls.customer = cls.api.customers.get_customer('1')
        cls.contact = cls.api.contacts.get_contact(1)

    def test_customer(self):
        self.assertIsInstance(self.customer, Customer)
        self.assertEqual(self.customer.name, 'ACME Corp.')
        self.assertEqual(self.customer.domains, 'acme.com')
        self.assertEqual(self.customer.cf_custom_key, 'custom_value')

    def test_customer_datetime(self):
        self.assertIsInstance(self.customer.created_at, datetime.datetime)
        self.assertIsInstance(self.customer.updated_at, datetime.datetime)

    def test_customer_str(self):
        self.assertEqual(str(self.customer), 'ACME Corp.')

    def test_customer_repr(self):
        self.assertEqual(repr(self.customer), '<Customer \'ACME Corp.\'>')

    def test_get_customer_from_contact(self):
        self.customer = self.api.customers.get_customer_from_contact(self.contact)
        self.test_customer()


class TestGroup(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = MockedAPI(DOMAIN, API_KEY)
        cls.group = cls.api.groups.get_group(1)

    def test_list_groups(self):
        groups = self.api.groups.list_groups()
        self.assertIsInstance(groups, list)
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[0].id, self.group.id)

    def test_group(self):
        self.assertIsInstance(self.group, Group)
        self.assertEqual(self.group.name, 'Entertainers')
        self.assertEqual(self.group.description, 'Singers dancers and stand up comedians')

    def test_group_datetime(self):
        self.assertIsInstance(self.group.created_at, datetime.datetime)
        self.assertIsInstance(self.group.updated_at, datetime.datetime)

    def test_group_str(self):
        self.assertEqual(str(self.group), 'Entertainers')

    def test_group_repr(self):
        self.assertEqual(repr(self.group), '<Group \'Entertainers\'>')

class TestRole(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = MockedAPI(DOMAIN, API_KEY)
        cls.role = cls.api.roles.get_role(1)

    def test_list_roles(self):
        roles = self.api.roles.list_roles()
        self.assertIsInstance(roles, list)
        self.assertEqual(len(roles), 2)
        self.assertEqual(roles[0].id, self.role.id)

    def test_role(self):
        self.assertIsInstance(self.role, Role)
        self.assertEqual(self.role.name, 'Agent')
        self.assertEqual(self.role.description, 'Can log, view, reply, update and resolve tickets and manage contacts.')

    def test_group_datetime(self):
        self.assertIsInstance(self.role.created_at, datetime.datetime)
        self.assertIsInstance(self.role.updated_at, datetime.datetime)

    def test_group_repr(self):
        self.assertEqual(repr(self.role), '<Role \'Agent\'>')


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

    def test_get_agent(self):
        self.assertIsInstance(self.agent, Agent)
        self.assertEqual(self.agent.id, 1)
        self.assertEqual(self.agent.contact['name'], 'Rachel')
        self.assertEqual(self.agent.contact['email'], 'rachel@freshdesk.com')
        self.assertEqual(self.agent.contact['mobile'], 1234)
        self.assertEqual(self.agent.contact['phone'], 5678)
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
        self.assertEqual(agent.contact['name'], 'Updated Name')
    
    def test_delete_agent(self):
        self.assertEquals(self.api.agents.delete_agent(1), None)

    def test_agent_name(self):
        self.assertEqual(self.agent.contact['name'], 'Rachel')
        
    def test_agent_mobile(self):
        self.assertEqual(self.agent.contact['mobile'], 1234)
    
    def test_agent_state(self):
        self.assertEqual(self.agent.available, True)
        self.assertEqual(self.agent.occasional, False)

    def test_agent_datetime(self):
        self.assertIsInstance(self.agent.created_at, datetime.datetime)
        self.assertIsInstance(self.agent.updated_at, datetime.datetime)

    def test_none_filter_name(self):
        agents = self.api.agents.list_agents()
        self.assertIsInstance(agents, list)
        self.assertEqual(len(agents), 2)
        self.assertEqual(agents[0].id, self.agent.id)
