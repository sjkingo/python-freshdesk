import requests

from freshdesk.models import Ticket

class API(object):
    def __init__(self, domain, api_key):
        """Creates a wrapper to perform API actions.

        Arguments:
          domain:    the Freshdesk domain (not custom). e.g. company.freshdesk.com
          api_key:   the API key
        """

        if domain[-1] == '/':
            domain[-1] = ''
        self.api_prefix = 'http://{}/helpdesk/'.format(domain)

        self.session = requests.Session()
        self.session.auth = (api_key, 'unused_with_api_key')
        self.session.headers = {'Content-Type': 'application/json'}

    def _get(self, url, params={}):
        """Wrapper around request.get() to use the API prefix. Returns a JSON response."""
        return self.session.get(self.api_prefix + url, params=params).json()

    def get_ticket(self, ticket_id):
        """Fetches the ticket for the given ticket ID"""
        url = 'tickets/%d.json' % ticket_id
        return Ticket(**self._get(url)['helpdesk_ticket'])

    def list_tickets(self, **kwargs):
        """List all tickets, optionally filtered by a view. Specify filters as
        keyword arguments, such as:

        filter_name = one of ['all_tickets', 'new_my_open', 'spam', 'deleted']
            (defaults to 'all_tickets')

        Multiple filters are AND'd together.
        """

        if 'filter_name' not in kwargs:
            kwargs['filter_name'] = 'all_tickets'

        url = 'tickets/filter/%s?format=json' % kwargs['filter_name']
        tickets = self._get(url, kwargs)
        return [Ticket(**t) for t in tickets]

    def list_all_tickets(self):
        """List all tickets, closed or open."""
        return self.list_tickets(filter_name='all_tickets')

    def list_open_tickets(self):
        """List all new and open tickets."""
        return self.list_tickets(filter_name='new_my_open')

    def list_deleted_tickets(self):
        """Lists all deleted tickets."""
        return self.list_tickets(filter_name='deleted')
