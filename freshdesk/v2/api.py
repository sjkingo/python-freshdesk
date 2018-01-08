import requests
from requests.exceptions import HTTPError
import json
from freshdesk.v2.models import Ticket, Comment, Customer, Contact, Group


class TicketAPI(object):
    def __init__(self, api):
        self._api = api

    def get_ticket(self, ticket_id):
        """Fetches the ticket for the given ticket ID"""
        url = 'tickets/%d' % ticket_id
        ticket = self._api._get(url)
        return Ticket(**ticket)

    def create_ticket(self, subject, **kwargs):
        """Creates a ticket"""
        url = 'tickets'
        status = kwargs.get('status', 2)
        priority = kwargs.get('priority', 1)
        data = {
            'subject': subject,
            'status': status,
            'priority': priority,
        }
        data.update(kwargs)
        ticket = self._api._post(url, data=json.dumps(data))
        return Ticket(**ticket)

    def create_outbound_email(self, subject, description, email,
                              email_config_id, **kwargs):
        """Creates an outbound email"""
        url = 'tickets/outbound_email'
        priority = kwargs.get('priority', 1)
        data = {
            'subject': subject,
            'description': description,
            'priority': priority,
            'email': email,
            'email_config_id': email_config_id,
        }
        data.update(kwargs)
        ticket = self._api._post(url, data=json.dumps(data))
        return Ticket(**ticket)

    def update_ticket(self, ticket_id, **kwargs):
        """Updates a ticket from a given ticket ID"""
        url = 'tickets/%d' % ticket_id
        ticket = self._api._put(url, data=json.dumps(kwargs))
        return Ticket(**ticket)

    def delete_ticket(self, ticket_id):
        """Delete the ticket for the given ticket ID"""
        url = 'tickets/%d' % ticket_id
        self._api._delete(url)

    def list_tickets(self, **kwargs):
        """List all tickets, optionally filtered by a view. Specify filters as
        keyword arguments, such as:

        filter_name = one of ['new_and_my_open', 'watching', 'spam', 'deleted',
                              None]
            (defaults to 'new_and_my_open')
            Passing None means that no named filter will be passed to
            Freshdesk, which mimics the behavior of the 'all_tickets' filter
            in v1 of the API.

        Multiple filters are AND'd together.
        """

        filter_name = 'new_and_my_open'
        if 'filter_name' in kwargs:
            filter_name = kwargs['filter_name']
            del kwargs['filter_name']

        url = 'tickets'
        if filter_name is not None:
            url += '?filter=%s&' % filter_name
        else:
            url += '?'
        page = 1
        per_page = 100
        tickets = []

        # Skip pagination by looping over each page and adding tickets
        while True:
            this_page = self._api._get(url + 'page=%d&per_page=%d'
                                       % (page, per_page), kwargs)
            tickets += this_page
            if len(this_page) < per_page:
                break
            page += 1

        return [Ticket(**t) for t in tickets]

    def list_new_and_my_open_tickets(self):
        """List all new and open tickets."""
        return self.list_tickets(filter_name='new_and_my_open')

    def list_watched_tickets(self):
        """List watched tickets, closed or open."""
        return self.list_tickets(filter_name='watching')

    def list_deleted_tickets(self):
        """Lists all deleted tickets."""
        return self.list_tickets(filter_name='deleted')


class CommentAPI(object):
    def __init__(self, api):
        self._api = api

    def list_comments(self, ticket_id):
        url = 'tickets/%d/conversations' % ticket_id
        comments = []
        for c in self._api._get(url):
            comments.append(Comment(**c))
        return comments

    def create_note(self, ticket_id, body, **kwargs):
        url = 'tickets/%d/notes' % ticket_id
        data = {'body': body}
        data.update(kwargs)
        return Comment(**self._api._post(url, data=json.dumps(data)))

    def create_reply(self, ticket_id, body, **kwargs):
        url = 'tickets/%d/reply' % ticket_id
        data = {'body': body}
        data.update(kwargs)
        return Comment(**self._api._post(url, data=json.dumps(data)))


class GroupAPI(object):
    def __init__(self, api):
        self._api = api

    def list_groups(self):
        url = 'groups'
        groups = []
        for g in self._api._get(url):
            groups.append(Group(**g))
        return groups

    def get_group(self, group_id):
        url = 'groups/%s' % group_id
        return Group(**self._api._get(url))


class ContactAPI(object):
    def __init__(self, api):
        self._api = api

    def get_contact(self, contact_id):
        url = 'contacts/%s' % contact_id
        return Contact(**self._api._get(url))


class CustomerAPI(object):
    def __init__(self, api):
        self._api = api

    def get_customer(self, company_id):
        url = 'customers/%s' % company_id
        return Customer(**self._api._get(url))

    def get_customer_from_contact(self, contact):
        return self.get_customer(contact.customer_id)


class API(object):
    def __init__(self, domain, api_key):
        """Creates a wrapper to perform API actions.

        Arguments:
          domain:    the Freshdesk domain (not custom). e.g. company.freshdesk.com
          api_key:   the API key

        Instances:
          .tickets:  the Ticket API
        """

        self._api_prefix = 'https://{}/api/v2/'.format(domain.rstrip('/'))
        self._session = requests.Session()
        self._session.auth = (api_key, 'unused_with_api_key')
        self._session.headers = {'Content-Type': 'application/json'}

        self.tickets = TicketAPI(self)
        self.comments = CommentAPI(self)
        self.contacts = ContactAPI(self)
        self.groups = GroupAPI(self)
        self.customers = CustomerAPI(self)

        if domain.find('freshdesk.com') < 0:
            raise AttributeError('Freshdesk v2 API works only via Freshdesk'
                                 'domains and not via custom CNAMEs')
        self.domain = domain

    def _action(self, req):
        try:
            j = req.json()
        except:
            req.raise_for_status()
            j = {}

        if 'error' in j:
            raise HTTPError('{}: {}'.format(j.get('description'),
                                            j.get('errors')))

        # Catch any other errors
        try:
            req.raise_for_status()
        except Exception as e:
            raise HTTPError("{}: {}".format(e, j))

        return j

    def _get(self, url, params={}):
        """Wrapper around request.get() to use the API prefix. Returns a JSON response."""
        req = self._session.get(self._api_prefix + url, params=params)
        return self._action(req)

    def _post(self, url, data={}):
        """Wrapper around request.post() to use the API prefix. Returns a JSON response."""
        req = self._session.post(self._api_prefix + url, data=data)
        return self._action(req)

    def _put(self, url, data={}):
        """Wrapper around request.put() to use the API prefix. Returns a JSON response."""
        req = self._session.put(self._api_prefix + url, data=data)
        return self._action(req)

    def _delete(self, url):
        """Wrapper around request.delete() to use the API prefix. Returns a JSON response."""
        req = self._session.delete(self._api_prefix + url)
        return self._action(req)
