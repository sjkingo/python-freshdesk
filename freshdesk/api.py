import requests
from requests.exceptions import HTTPError
from json import dumps
from freshdesk.models import *


class TicketAPI(object):

    def __init__(self, api):
        self._api = api

    def get_ticket(self, ticket_id):
        """Fetches the ticket for the given ticket ID"""
        url = 'helpdesk/tickets/%d.json' % ticket_id
        return Ticket(**self._api._get(url)['helpdesk_ticket'])

    def create_ticket(self, description, subject, email, priority=1, status=2):
        url = 'helpdesk/tickets.json'
        data = {
            "helpdesk_ticket": {
                "description": description,
                "subject": subject,
                "email": email,
                "priority": priority,
                "status": status
            },
            "cc_emails": "mmukesh95@hotmail.com"

        }

        return Ticket(**self._api._post(url, data=dumps(data))['helpdesk_ticket'])

    def list_tickets(self, **kwargs):
        """List all tickets, optionally fi1ltered by a view. Specify filters as
        keyword arguments, such as:

        filter_name = one of ['all_tickets', 'new_my_open', 'spam', 'deleted']
            (defaults to 'all_tickets')

        Multiple filters are AND'd together.
        """

        filter_name = 'all_tickets'
        if 'filter_name' in kwargs:
            filter_name = kwargs['filter_name']
            del kwargs['filter_name']

        url = 'helpdesk/tickets/filter/%s?format=json' % filter_name
        page = 1
        tickets = []

        # Skip pagination by looping over each page and adding tickets
        while True:
            this_page = self._api._get(url + '&page=%d' % page, kwargs)
            if len(this_page) == 0:
                break
            tickets += this_page
            page += 1

        return [self.get_ticket(t['display_id']) for t in tickets]

    def list_all_tickets(self):
        """List all tickets, closed or open."""
        return self.list_tickets(filter_name='all_tickets')

    def list_open_tickets(self):
        """List all new and open tickets."""
        return self.list_tickets(filter_name='new_my_open')

    def list_deleted_tickets(self):
        """Lists all deleted tickets."""
        return self.list_tickets(filter_name='deleted')


class ContactAPI(object):

    def __init__(self, api):
        self._api = api

    def get_contact(self, contact_id):
        url = 'contacts/%s.json' % contact_id
        return Contact(**self._api._get(url)['user'])


class API(object):

    def __init__(self, domain, api_key):
        """Creates a wrapper to perform API actions.

        Arguments:
          domain:    the Freshdesk domain (not custom). e.g. company.freshdesk.com
          api_key:   the API key

        Instances:
          .tickets:  the Ticket API
        """

        self._api_prefix = 'https://{}/'.format(domain.rstrip('/'))
        self._session = requests.Session()
        self._session.auth = (api_key, 'unused_with_api_key')
        self._session.headers = {'Content-Type': 'application/json'}

        self.tickets = TicketAPI(self)
        self.contacts = ContactAPI(self)

    def _get(self, url, params={}):
        """Wrapper around request.get() to use the API prefix. Returns a JSON response."""
        r = self._session.get(self._api_prefix + url, params=params)
        r.raise_for_status()

        if 'Retry-After' in r.headers:
            raise HTTPError('403 Forbidden: API rate-limit has been reached until {}.'
                            'See http://freshdesk.com/api#ratelimit'.format(r.headers['Retry-After']))
        j = r.json()
        if 'require_login' in j:
            raise HTTPError(
                '403 Forbidden: API key is incorrect for this domain')
        return r.json()

    def _post(self, url, data={}):
        """Wrapper around request.post() to use the API prefix. Returns a JSON response."""
        r = self._session.post(self._api_prefix + url, data=data)
        r.raise_for_status()
        if 'Retry-After' in r.headers:
            raise HTTPError('403 Forbidden: API rate-limit has been reached until {}.'
                            'See http://freshdesk.com/api#ratelimit'.format(r.headers['Retry-After']))
        j = r.json()
        if 'require_login' in j:
            raise HTTPError(
                '403 Forbidden: API key is incorrect for this domain')
        return r.json()
