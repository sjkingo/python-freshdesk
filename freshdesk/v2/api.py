import requests
from requests.exceptions import HTTPError
import json
from freshdesk.v2.models import Ticket, Comment, Customer, Contact, Group, Company, Agent, Role, TicketField


class TicketAPI(object):
    def __init__(self, api):
        self._api = api

    def get_ticket(self, ticket_id):
        """Fetches the ticket for the given ticket ID"""
        url = 'tickets/%d' % ticket_id
        ticket = self._api._get(url)
        return Ticket(**ticket)

    def create_ticket(self, subject, **kwargs):
        """
            Creates a ticket
            To create ticket with attachments,
            pass a key 'attachments' with value as list of fully qualified file paths in string format.
            ex: attachments = ('/path/to/attachment1', '/path/to/attachment2')
        """

        url = 'tickets'
        status = kwargs.get('status', 2)
        priority = kwargs.get('priority', 1)
        data = {
            'subject': subject,
            'status': status,
            'priority': priority,
        }
        data.update(kwargs)
        if 'attachments' in data:
            ticket = self._create_ticket_with_attachment(url, data)
            return Ticket(**ticket)

        ticket = self._api._post(url, data=json.dumps(data))
        return Ticket(**ticket)

    def _create_ticket_with_attachment(self, url, data):
        attachments = data['attachments']
        del data['attachments']
        multipart_data = []

        for attachment in attachments:
            file_name = attachment.split("/")[-1:][0]
            multipart_data.append(('attachments[]', (file_name, open(attachment), None)))

        ticket = self._api._post(url, data=data, files=multipart_data)
        return ticket

    def create_outbound_email(self, subject, description, email, email_config_id, **kwargs):
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
        page = 1 if not 'page' in kwargs else kwargs['page']
        per_page = 100 if not 'per_page' in kwargs else kwargs['per_page']
        tickets = []

        # Skip pagination by looping over each page and adding tickets if 'page' key is not in kwargs.
        # else return the requested page and break the loop
        while True:
            this_page = self._api._get(url + 'page=%d&per_page=%d'
                                       % (page, per_page), kwargs)
            tickets += this_page
            if len(this_page) < per_page or 'page' in kwargs:
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

    def list_groups(self, **kwargs):
        url = 'groups?'
        page = 1 if not 'page' in kwargs else kwargs['page']
        per_page = 100 if not 'per_page' in kwargs else kwargs['per_page']

        groups = []
        while True:
            this_page = self._api._get(url + 'page=%d&per_page=%d'
                                       % (page, per_page), kwargs)
            groups += this_page
            if len(this_page) < per_page or 'page' in kwargs:
                break
            page += 1

        return [Group(**g) for g in groups]

    def get_group(self, group_id):
        url = 'groups/%s' % group_id
        return Group(**self._api._get(url))


class ContactAPI(object):
    def __init__(self, api):
        self._api = api

    def list_contacts(self, **kwargs):
        """
        List all contacts, optionally filtered by a query. Specify filters as
        query keyword argument, such as:

        email=abc@xyz.com,
        mobile=1234567890,
        phone=1234567890,

        contacts can be filtered by state and company_id such as:

        state=[blocked/deleted/unverified/verified]
        company_id=1234

        contacts updated after a timestamp can be filtered such as;

        _updated_since=2018-01-19T02:00:00Z

        Passing None means that no named filter will be passed to
        Freshdesk, which returns list of all contacts

        """

        url = 'contacts?'
        page = 1 if not 'page' in kwargs else kwargs['page']
        per_page = 100 if not 'per_page' in kwargs else kwargs['per_page']

        contacts = []

        # Skip pagination by looping over each page and adding tickets if 'page' key is not in kwargs.
        # else return the requested page and break the loop
        while True:
            this_page = self._api._get(url + 'page=%d&per_page=%d'
                                       % (page, per_page), kwargs)
            contacts += this_page
            if len(this_page) < per_page or 'page' in kwargs:
                break

            page += 1

        return [Contact(**c) for c in contacts]

    def create_contact(self, *args, **kwargs):
        """Creates a contact"""
        url = 'contacts'
        data = {
            'view_all_tickets': False,
            'description': 'Freshdesk Contact'
        }
        data.update(kwargs)
        return Contact(**self._api._post(url, data=json.dumps(data)))

    def get_contact(self, contact_id):
        url = 'contacts/%d' % contact_id
        return Contact(**self._api._get(url))

    def update_contact(self, contact_id, **data):
        url = 'contacts/%d' % contact_id
        return Contact(**self._api._put(url, data=json.dumps(data)))

    def soft_delete_contact(self, contact_id):
        url = 'contacts/%d' % contact_id
        self._api._delete(url)

    def restore_contact(self, contact_id):
        url = 'contacts/%d/restore' % contact_id
        self._api._put(url)

    def permanently_delete_contact(self, contact_id, force=True):
        url = 'contacts/%d/hard_delete?force=%r' % (contact_id, force)
        self._api._delete(url)

    def make_agent(self, contact_id, **kwargs):
        url = 'contacts/%d/make_agent' % contact_id
        data = {
            'occasional': False,
            'ticket_scope': 2,
        }
        data.update(kwargs)
        contact = self._api._put(url, data=json.dumps(data))
        return self._api.agents.get_agent(contact['agent']['id'])


class CustomerAPI(object):
    def __init__(self, api):
        self._api = api

    def get_customer(self, company_id):
        url = 'customers/%s' % company_id
        return Customer(**self._api._get(url))

    def get_customer_from_contact(self, contact):
        return self.get_customer(contact.customer_id)


class CompanyAPI(object):
    def __init__(self, api):
        self._api = api

    def get_company(self, company_id):
        url = 'companies/%s' % company_id
        return Company(**self._api._get(url))


class RoleAPI(object):
    def __init__(self, api):
        self._api = api

    def list_roles(self):
        url = 'roles'
        roles = []
        for r in self._api._get(url):
            roles.append(Role(**r))
        return roles

    def get_role(self, role_id):
        url = 'roles/%s' % role_id
        return Role(**self._api._get(url))


class TicketFieldAPI(object):
    def __init__(self, api):
        self._api = api

    def list_ticket_fields(self, **kwargs):
        url = 'ticket_fields'
        ticket_fields = []

        if kwargs.has_key('type'):
            url = "{}?type={}".format(url, kwargs['type'])

        for tf in self._api._get(url):
            ticket_fields.append(TicketField(**tf))
        return ticket_fields


class AgentAPI(object):
    def __init__(self, api):
        self._api = api

    def list_agents(self, **kwargs):
        """List all agents, optionally filtered by a view. Specify filters as
        keyword arguments, such as:

        {
            email='abc@xyz.com',
            phone=873902,
            mobile=56523,
            state='fulltime'
        }

        Passing None means that no named filter will be passed to
        Freshdesk, which returns list of all agents

        Multiple filters are AND'd together.
        """

        url = 'agents?'
        page = 1 if not 'page' in kwargs else kwargs['page']
        per_page = 100 if not 'per_page' in kwargs else kwargs['per_page']

        agents = []

        # Skip pagination by looping over each page and adding tickets if 'page' key is not in kwargs.
        # else return the requested page and break the loop
        while True:
            this_page = self._api._get(url + 'page=%d&per_page=%d'
                                       % (page, per_page), kwargs)
            agents += this_page
            if len(this_page) < per_page or 'page' in kwargs:
                break
            page += 1

        return [Agent(**a) for a in agents]

    def get_agent(self, agent_id):
        """Fetches the agent for the given agent ID"""
        url = 'agents/%s' % agent_id
        return Agent(**self._api._get(url))

    def update_agent(self, agent_id, **kwargs):
        """Updates an agent"""
        url = 'agents/%s' % agent_id
        agent = self._api._put(url, data=json.dumps(kwargs))
        return Agent(**agent)

    def delete_agent(self, agent_id):
        """Delete the agent for the given agent ID"""
        url = 'agents/%d' % agent_id
        self._api._delete(url)

    def currently_authenticated_agent(self):
        """Fetches currently logged in agent"""
        url = 'agents/me'
        return Agent(**self._api._get(url))


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
        self.companies = CompanyAPI(self)
        self.groups = GroupAPI(self)
        self.customers = CustomerAPI(self)
        self.agents = AgentAPI(self)
        self.roles = RoleAPI(self)
        self.ticket_fields = TicketFieldAPI(self)

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

        if 'Retry-After' in req.headers:
            raise HTTPError('429 Rate Limit Exceeded: API rate-limit has been reached until {} seconds.'
                            'See http://freshdesk.com/api#ratelimit'.format(req.headers['Retry-After']))

        if 'code' in j and j['code'] == "invalid_credentials":
            raise HTTPError('401 Unauthorized: Please login with correct credentials')

        if 'errors' in j:
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

    def _post(self, url, data={}, **kwargs):
        """Wrapper around request.post() to use the API prefix. Returns a JSON response."""
        if 'files' in kwargs:
            req = requests.post(self._api_prefix + url, auth=self._session.auth, data=data, **kwargs)
            return self._action(req)

        req = self._session.post(self._api_prefix + url, data=data, **kwargs)
        return self._action(req)

    def _put(self, url, data={}):
        """Wrapper around request.put() to use the API prefix. Returns a JSON response."""
        req = self._session.put(self._api_prefix + url, data=data)
        return self._action(req)

    def _delete(self, url):
        """Wrapper around request.delete() to use the API prefix. Returns a JSON response."""
        req = self._session.delete(self._api_prefix + url)
        return self._action(req)
