import json
import os.path
import re

import pytest

from freshdesk.v2.api import API

DOMAIN = 'pythonfreshdesk.freshdesk.com'
API_KEY = 'MX4CEAw4FogInimEdRW2'


class MockedAPI(API):
    def __init__(self, *args):
        self.resolver = {
            'get': {
                re.compile(r'tickets\?filter=new_and_my_open&page=1&per_page=100'): self.read_test_file(
                    'all_tickets.json'),
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
                re.compile(r'search/tickets\?page=1&query="tag:\'mytag\'"'): self.read_test_file('search_tickets.json'),
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


@pytest.fixture()
def api():
    return MockedAPI(DOMAIN, API_KEY)
