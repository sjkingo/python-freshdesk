import json
import os.path
import re

import pytest

from freshdesk.v1.api import API

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


@pytest.fixture()
def api():
    return MockedAPI(DOMAIN, API_KEY)
