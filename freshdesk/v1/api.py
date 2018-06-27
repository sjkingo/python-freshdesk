import requests
import json
from requests.exceptions import HTTPError
from freshdesk.v1.models import Ticket, Contact, Agent, Customer, TimeEntry


class TicketAPI(object):
    def __init__(self, api):
        self._api = api

    def create_ticket(self, subject, **kwargs):
        url = 'helpdesk/tickets.json'
        status = kwargs.get('status', 2)
        priority = kwargs.get('priority', 1)
        cc_emails = ','.join(kwargs.get('cc_emails', []))
        ticket_data = {
            'subject': subject,
            'status': status,
            'priority': priority,
        }
        ticket_data.update(kwargs)
        data = {
            'helpdesk_ticket': ticket_data,
            'cc_emails': cc_emails,
        }
        
        return Ticket(**self._api._post(url, data=data)['helpdesk_ticket'])

    def get_ticket(self, ticket_id):
        """Fetches the ticket for the given ticket ID"""
        url = 'helpdesk/tickets/%d.json' % ticket_id
        return Ticket(**self._api._get(url)['helpdesk_ticket'])

    def list_tickets(self, **kwargs):
        """List all tickets, optionally filtered by a view. Specify filters as
        keyword arguments, such as:

        filter_name = one of ['all_tickets', 'new_my_open', 'spam', 'deleted',
                               None]
            (defaults to 'all_tickets'; passing None uses the default)

        Multiple filters are AND'd together.
        """

        filter_name = 'all_tickets'
        if 'filter_name' in kwargs and kwargs['filter_name'] is not None:
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

    def list_contacts(self, **kwargs):
        """
        List all contacts, optionally filtered by a query. Specify filters as
        query keyword argument, such as: 
        
        query= email is abc@xyz.com,
        query= mobile is 1234567890,
        query= phone is 1234567890,

        contacts can be filtered by name such as;
        
        letter=Prenit

        Passing None means that no named filter will be passed to
        Freshdesk, which returns list of all contacts

        """

        url = 'contacts.json?'
        if 'query' in kwargs.keys():
            filter_query = kwargs.pop('query')
            url = url + "query={}".format(filter_query)

        if 'state' in kwargs.keys():
            state_query = kwargs.pop('state')
            url = url + "state={}".format(state_query)    

        if 'letter' in kwargs.keys():
            name_query = kwargs.pop('letter')
            url = url + "letter={}".format(name_query)        
                
        contacts = self._api._get(url)    
        return [Contact(**c['user']) for c in contacts]

    def create_contact(self, *args, **kwargs):
        """Creates a contact"""
        url = 'contacts.json'
        contact_data = {
            'active': True,
            'helpdesk_agent': False,
            'description': 'Freshdesk Contact'
        }
        contact_data.update(kwargs)
        payload = {
            'user': contact_data
        }

        return Contact(**self._api._post(url, data=payload)['user'])
     
    def make_agent(self, contact_id):
        url = 'contacts/%d/make_agent.json' % contact_id
        agent = self._api._put(url)['agent']
        return self._api.agents.get_agent(agent['id'])

    def get_contact(self, contact_id):
        url = 'contacts/%d.json' % contact_id
        return Contact(**self._api._get(url)['user'])

    def delete_contact(self, contact_id):
        url = 'contacts/%d.json' % contact_id
        self._api._delete(url)


class AgentAPI(object):
    def __init__(self, api):
        self._api = api

    def list_agents(self, **kwargs):
        """List all agents, optionally filtered by a query. Specify filters as
        query keyword argument, such as: 
        
        query= email is abc@xyz.com,
        query= mobile is 1234567890,
        query= phone is 1234567890,

        agents can be filtered by state such as:
        
        state=active/occasional

        Passing None means that no named filter will be passed to
        Freshdesk, which returns list of all agents 

        """

        url = 'agents.json?'
        if 'query' in kwargs.keys():
            filter_query = kwargs.pop('query')
            url = url + "query={}".format(filter_query)

        if 'state' in kwargs.keys():
            state_query = kwargs.pop('state')
            url = url + "state={}".format(state_query)    
                
        agents = self._api._get(url)    
        return [Agent(**a['agent']) for a in agents]
    
    def get_agent(self, agent_id):
        """Fetches the agent for the given agent ID"""    
        url = 'agents/%s.json' % agent_id
        return Agent(**self._api._get(url)['agent'])   
            
    def update_agent(self, agent_id, **kwargs):
        """Updates an agent"""
        url = 'agents/%s.json' % agent_id
        agent = self._api._put(url, data=json.dumps(kwargs))['agent']
        return Agent(**agent)

    def delete_agent(self, agent_id):
        """Delete the agent for the given agent ID"""
        url = 'agents/%d.json' % agent_id
        self._api._delete(url)


class CustomerAPI(object):
    def __init__(self, api):
        self._api = api

    def get_customer(self, company_id):
        url = 'customers/%s.json' % company_id
        return Customer(**self._api._get(url)['customer'])

    def get_customer_from_contact(self, contact):
        return self.get_customer(contact.customer_id)


class TimeAPI(object):
    def __init__(self, api):
        self._api = api

    def get_all_timesheets(self, **kwargs):
        url = 'helpdesk/time_sheets.json'
        if "filter_name" in kwargs.keys() and "filter_value" in kwargs.keys():
            url = url + "?{}={}".format(kwargs["filter_name"], kwargs["filter_value"])
        l = []
        timesheet_data = self._api._get(url)
        i = 0
        while (i < len(timesheet_data)):
            l.append(TimeEntry(**timesheet_data[i]['time_entry']))
            i = i + 1
        return l

    def get_timesheet_by_ticket(self, ticket_id):
        url = 'helpdesk/tickets/%s/time_sheets.json' % ticket_id
        l = []
        timesheet_data = self._api._get(url)
        i = 0
        while (i < len(timesheet_data)):
            l.append(TimeEntry(**timesheet_data[i]['time_entry']))
            i = i + 1
        return l


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
        self.auth = (api_key, 'X')
        self.headers = {'Content-Type': 'application/json'}

        self.tickets = TicketAPI(self)
        self.contacts = ContactAPI(self)
        self.agents = AgentAPI(self)
        self.timesheets = TimeAPI(self)
        self.customers = CustomerAPI(self)

    def _get(self, url, params={}):
        """Wrapper around request.get() to use the API prefix. Returns a JSON response."""
        r = requests.get(self._api_prefix + url,
            params=params,
            headers=self.headers,
            auth=self.auth,
        )
        return self._action(r)

    def _post(self, url, data={}):
        """Wrapper around request.post() to use the API prefix. Returns a JSON response."""
        r = requests.post(self._api_prefix + url,
            data=json.dumps(data),
            headers=self.headers,
            auth=self.auth,
            allow_redirects=False,
        )
        return self._action(r)        
    
    def _put(self, url, data={}):
        """Wrapper around request.put() to use the API prefix. Returns a JSON response."""
        r = requests.put(self._api_prefix + url,
            data=json.dumps(data),
            headers=self.headers,
            auth=self.auth,
            allow_redirects=False,
        )
        return self._action(r)

    def _delete(self, url):
        """Wrapper around request.delete() to use the API prefix. Returns a JSON response."""
        r = requests.delete(self._api_prefix + url,
            headers=self.headers,
            auth=self.auth,
            allow_redirects=False,
        )
        return self._action(r)    

    def _action(self, res):
        """Returns JSON response or raise exception if errors are present"""
        try:
            j = res.json()
        except:
            res.raise_for_status()
            j = {}

        if 'Retry-After' in res.headers:
            raise HTTPError('403 Forbidden: API rate-limit has been reached until {}.'
                            'See http://freshdesk.com/api#ratelimit'.format(res.headers['Retry-After']))

        if 'require_login' in j:
            raise HTTPError('403 Forbidden: API key is incorrect for this domain')

        if 'error' in j:
            raise HTTPError('{}: {}'.format(j.get('description'),
                                            j.get('errors')))

        # Catch any other errors
        try:
            res.raise_for_status()
        except Exception as e:
            raise HTTPError("{}: {}".format(e, j))

        return j
