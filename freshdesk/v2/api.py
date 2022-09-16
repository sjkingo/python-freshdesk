import json

import requests
from requests import HTTPError

from freshdesk.v2.errors import (
    FreshdeskAccessDenied,
    FreshdeskBadRequest,
    FreshdeskError,
    FreshdeskNotFound,
    FreshdeskRateLimited,
    FreshdeskServerError,
    FreshdeskUnauthorized,
)
from freshdesk.v2.models import (
    Agent,
    Comment,
    Company,
    Contact,
    Customer,
    Group,
    Role,
    Ticket,
    TicketField,
    TimeEntry,
    SolutionCategory,
    SolutionFolder,
    SolutionArticle,
)


class TicketAPI(object):
    def __init__(self, api):
        self._api = api

    def get_ticket(self, ticket_id, *include):
        """
        Fetches the ticket for the given ticket ID
        You can pass strings for the include parameter and they'll be included as include params to the request
        ex: get_ticket(some_id, "stats", "conversations", "requester", "company") will result in the following request:
        tickets/[some_id]?include=stats,conversations,requester,company
        """
        url = "tickets/%d%s" % (ticket_id, "?include=%s" % ",".join(include) if include else "")
        ticket = self._api._get(url)
        return Ticket(**ticket)

    def create_ticket(self, subject, **kwargs):
        """
        Creates a ticket
        To create ticket with attachments,
        pass a key 'attachments' with value as list of fully qualified file paths in string format.
        ex: attachments = ('/path/to/attachment1', '/path/to/attachment2')
        """

        url = "tickets"
        status = kwargs.get("status", 2)
        priority = kwargs.get("priority", 1)
        data = {
            "subject": subject,
            "status": status,
            "priority": priority,
        }
        data.update(kwargs)
        if "attachments" in data:
            ticket = self._create_ticket_with_attachment(url, data)
            return Ticket(**ticket)

        ticket = self._api._post(url, data=json.dumps(data))
        return Ticket(**ticket)

    def _create_ticket_with_attachment(self, url, data):
        attachments = data["attachments"]
        del data["attachments"]
        multipart_data = []

        for attachment in attachments:
            file_name = attachment.split("/")[-1:][0]
            multipart_data.append(("attachments[]", (file_name, open(attachment, "rb"), None)))

        for key, value in data.copy().items():
            # Reformat ticket properties to work with the multipart/form-data encoding.
            if isinstance(value, list) and not key.endswith("[]"):
                data[key + "[]"] = value
                del data[key]

        if "custom_fields" in data and isinstance(data["custom_fields"], dict):
            # Reformat custom fields to work with the multipart/form-data encoding.
            for field, value in data["custom_fields"].items():
                data["custom_fields[{}]".format(field)] = value
            del data["custom_fields"]

        # Override the content type so that `requests` correctly sets it to multipart/form-data instead of JSON.
        ticket = self._api._post(url, data=data, files=multipart_data, headers={"Content-Type": None})
        return ticket

    def create_outbound_email(self, subject, description, email, email_config_id, **kwargs):
        """Creates an outbound email"""
        url = "tickets/outbound_email"
        priority = kwargs.get("priority", 1)
        data = {
            "subject": subject,
            "description": description,
            "priority": priority,
            "email": email,
            "email_config_id": email_config_id,
        }
        data.update(kwargs)
        ticket = self._api._post(url, data=json.dumps(data))
        return Ticket(**ticket)

    def update_ticket(self, ticket_id, **kwargs):
        """Updates a ticket from a given ticket ID"""
        url = "tickets/%d" % ticket_id
        ticket = self._api._put(url, data=json.dumps(kwargs))
        return Ticket(**ticket)

    def delete_ticket(self, ticket_id):
        """Delete the ticket for the given ticket ID"""
        url = "tickets/%d" % ticket_id
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

        filter_name = "new_and_my_open"
        if "filter_name" in kwargs:
            filter_name = kwargs["filter_name"]
            del kwargs["filter_name"]

        url = "tickets"
        if filter_name is not None:
            url += "?filter=%s&" % filter_name
        else:
            url += "?"

        if "updated_since" in kwargs:
            url += "updated_since=%s&" % kwargs["updated_since"]

        page = kwargs.get("page", 1)
        per_page = kwargs.get("per_page", 100)

        tickets = []

        # Skip pagination by looping over each page and adding tickets if 'page' key is not in kwargs.
        # else return the requested page and break the loop
        while True:
            this_page = self._api._get(url + "page=%d&per_page=%d" % (page, per_page), kwargs)
            tickets += this_page
            if len(this_page) < per_page or "page" in kwargs:
                break
            page += 1

        return [Ticket(**t) for t in tickets]

    def list_new_and_my_open_tickets(self):
        """List all new and open tickets."""
        return self.list_tickets(filter_name="new_and_my_open")

    def list_watched_tickets(self):
        """List watched tickets, closed or open."""
        return self.list_tickets(filter_name="watching")

    def list_deleted_tickets(self):
        """Lists all deleted tickets."""
        return self.list_tickets(filter_name="deleted")

    def filter_tickets(self, query, **kwargs):
        """Filter tickets by a given query string. The query string must be in
        the format specified in the API documentation at:
          https://developer.freshdesk.com/api/#filter_tickets

        query = "(ticket_field:integer OR ticket_field:'string') AND ticket_field:boolean"
        """
        if len(query) > 512:
            raise AttributeError("Query string can have up to 512 characters")

        url = "search/tickets?"
        page = kwargs.get("page", 1)
        per_page = 30

        tickets = []
        while True:
            this_page = self._api._get(url + 'page={}&query="{}"'.format(page, query), kwargs)
            this_page = this_page["results"]
            tickets += this_page
            if len(this_page) < per_page or page == 10 or "page" in kwargs:
                break
            page += 1

        return [Ticket(**t) for t in tickets]


class CommentAPI(object):
    def __init__(self, api):
        self._api = api

    def list_comments(self, ticket_id, **kwargs):
        url = "tickets/%d/conversations?" % ticket_id
        page = kwargs.get("page", 1)
        per_page = kwargs.get("per_page", 100)

        comments = []

        # Skip pagination by looping over each page and adding comments if 'page' key is not in kwargs.
        # else return the requested page and break the loop
        while True:
            this_page = self._api._get(url + "page=%d&per_page=%d" % (page, per_page), kwargs)
            comments += this_page
            if len(this_page) < per_page or "page" in kwargs:
                break
            page += 1

        return [Comment(**c) for c in comments]

    def create_note(self, ticket_id, body, **kwargs):
        url = "tickets/%d/notes" % ticket_id
        data = {"body": body}
        data.update(kwargs)
        return Comment(**self._api._post(url, data=json.dumps(data)))

    def create_reply(self, ticket_id, body, **kwargs):
        url = "tickets/%d/reply" % ticket_id
        data = {"body": body}
        data.update(kwargs)
        return Comment(**self._api._post(url, data=json.dumps(data)))


class GroupAPI(object):
    def __init__(self, api):
        self._api = api

    def list_groups(self, **kwargs):
        url = "groups?"
        page = kwargs.get("page", 1)
        per_page = kwargs.get("per_page", 100)

        groups = []
        while True:
            this_page = self._api._get(url + "page=%d&per_page=%d" % (page, per_page), kwargs)
            groups += this_page
            if len(this_page) < per_page or "page" in kwargs:
                break
            page += 1

        return [Group(**g) for g in groups]

    def get_group(self, group_id):
        url = "groups/%s" % group_id
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

        url = "contacts?"
        page = kwargs.get("page", 1)
        per_page = kwargs.get("per_page", 100)

        contacts = []

        # Skip pagination by looping over each page and adding tickets if 'page' key is not in kwargs.
        # else return the requested page and break the loop
        while True:
            this_page = self._api._get(url + "page=%d&per_page=%d" % (page, per_page), kwargs)
            contacts += this_page
            if len(this_page) < per_page or "page" in kwargs:
                break

            page += 1

        return [Contact(**c) for c in contacts]

    def filter_contacts(self, query, **kwargs):
        """Filter contacts by a given query string. The query string must be in
        the format specified in the API documentation at:
          https://developers.freshdesk.com/api/#filter_contacts

        query = "(contact_field:integer OR contact_field:'string') AND contact_field:boolean"
        """
        if len(query) > 512:
            raise AttributeError("Query string can have up to 512 characters")

        url = "search/contacts?"
        page = kwargs.get("page", 1)
        per_page = 30

        contacts = []
        while True:
            this_page = self._api._get(
                url + 'page={}&query="{}"'.format(page, query), kwargs
            )
            this_page = this_page["results"]
            contacts += this_page
            if len(this_page) < per_page or page == 10 or "page" in kwargs:
                break
            page += 1

        return [Contact(**c) for c in contacts]

    def create_contact(self, *args, **kwargs):
        """Creates a contact"""
        url = "contacts"
        data = {"view_all_tickets": False, "description": "Freshdesk Contact"}
        data.update(kwargs)
        return Contact(**self._api._post(url, data=json.dumps(data)))

    def get_contact(self, contact_id):
        url = "contacts/%d" % contact_id
        return Contact(**self._api._get(url))

    def update_contact(self, contact_id, **data):
        url = "contacts/%d" % contact_id
        return Contact(**self._api._put(url, data=json.dumps(data)))

    def soft_delete_contact(self, contact_id):
        url = "contacts/%d" % contact_id
        self._api._delete(url)

    def restore_contact(self, contact_id):
        url = "contacts/%d/restore" % contact_id
        self._api._put(url)

    def permanently_delete_contact(self, contact_id, force=True):
        url = "contacts/%d/hard_delete?force=%r" % (contact_id, force)
        self._api._delete(url)

    def make_agent(self, contact_id, **kwargs):
        url = "contacts/%d/make_agent" % contact_id
        data = {
            "occasional": False,
            "ticket_scope": 2,
        }
        data.update(kwargs)
        contact = self._api._put(url, data=json.dumps(data))
        return self._api.agents.get_agent(contact["agent"]["id"])


class CustomerAPI(object):
    def __init__(self, api):
        self._api = api

    def get_customer(self, company_id):
        url = "customers/%s" % company_id
        return Customer(**self._api._get(url))

    def get_customer_from_contact(self, contact):
        return self.get_customer(contact.customer_id)


class CompanyAPI(object):
    def __init__(self, api):
        self._api = api

    def get_company(self, company_id):
        url = "companies/%s" % company_id
        return Company(**self._api._get(url))

    def list_companies(self, **kwargs):
        url = "companies?"
        page = kwargs.get("page", 1)
        per_page = kwargs.get("per_page", 100)

        companies = []

        # Skip pagination by looping over each page and adding companies if 'page' key is not in kwargs.
        # else return the requested page and break the loop
        while True:
            this_page = self._api._get(url + "page=%d&per_page=%d" % (page, per_page), kwargs)
            companies += this_page
            if len(this_page) < per_page or "page" in kwargs:
                break

            page += 1

        return [Company(**c) for c in companies]

    def filter_companies(self, query, **kwargs):
        """Filter companies by a given query string. The query string must be in
        the format specified in the API documentation at:
          https://developers.freshdesk.com/api/#filter_companies

        query = "(company_field:integer OR company_field:'string') AND company_field:boolean"
        """
        if len(query) > 512:
            raise AttributeError("Query string can have up to 512 characters")

        url = "search/companies?"
        page = kwargs.get("page", 1)
        per_page = 30

        companies = []
        while True:
            this_page = self._api._get(url + 'page={}&query="{}"'.format(page, query), kwargs)
            this_page = this_page["results"]
            companies += this_page
            if len(this_page) < per_page or page == 10 or "page" in kwargs:
                break
            page += 1

        return [Company(**c) for c in companies]

    def delete_company(self, company_id):
        """Delete the company for the given company ID"""
        url = "companies/%d" % company_id
        self._api._delete(url)

    def create_company(self, *args, **kwargs):
        """Creates a company"""
        url = "companies"
        return Company(**self._api._post(url, data=json.dumps(kwargs)))

    def update_company(self, company_id, **data):
        url = "companies/%d" % company_id
        return Company(**self._api._put(url, data=json.dumps(data)))

class RoleAPI(object):
    def __init__(self, api):
        self._api = api

    def list_roles(self):
        url = "roles"
        roles = []
        for r in self._api._get(url):
            roles.append(Role(**r))
        return roles

    def get_role(self, role_id):
        url = "roles/%s" % role_id
        return Role(**self._api._get(url))


class TimeEntryAPI(object):
    def __init__(self, api):
        self._api = api

    def list_time_entries(self, ticket_id=None, **kwargs):
        url = "time_entries?"

        if ticket_id is not None:
            url = "tickets/%d/time_entries?" % ticket_id

        page = kwargs.get("page", 1)
        per_page = kwargs.get("per_page", 100)

        time_entries = []

        # Skip pagination by looping over each page and adding tickets if 'page' key is not in kwargs.
        # else return the requested page and break the loop
        while True:
            this_page = self._api._get(url + 'page={}&per_page={}'.format(page, per_page), kwargs)
            time_entries += this_page
            if len(this_page) < per_page or "page" in kwargs:
                break

            page += 1

        return [TimeEntry(**c) for c in time_entries]


class TicketFieldAPI(object):
    def __init__(self, api):
        self._api = api

    def list_ticket_fields(self, **kwargs):
        url = "ticket_fields"
        ticket_fields = []

        if "type" in kwargs:
            url = "{}?type={}".format(url, kwargs["type"])

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

        url = "agents?"
        page = kwargs.get("page", 1)
        per_page = kwargs.get("per_page", 100)

        agents = []

        # Skip pagination by looping over each page and adding tickets if 'page' key is not in kwargs.
        # else return the requested page and break the loop
        while True:
            this_page = self._api._get(url + "page=%d&per_page=%d" % (page, per_page), kwargs)
            agents += this_page
            if len(this_page) < per_page or "page" in kwargs:
                break
            page += 1

        return [Agent(**a) for a in agents]

    def get_agent(self, agent_id):
        """Fetches the agent for the given agent ID"""
        url = "agents/%s" % agent_id
        return Agent(**self._api._get(url))

    def update_agent(self, agent_id, **kwargs):
        """Updates an agent"""
        url = "agents/%s" % agent_id
        agent = self._api._put(url, data=json.dumps(kwargs))
        return Agent(**agent)

    def delete_agent(self, agent_id):
        """Delete the agent for the given agent ID"""
        url = "agents/%d" % agent_id
        self._api._delete(url)

    def currently_authenticated_agent(self):
        """Fetches currently logged in agent"""
        url = "agents/me"
        return Agent(**self._api._get(url))


class SolutionCategoryAPI(object):
    def __init__(self, api):
        self._api = api

    def list_categories(self):
        url = "solutions/categories"
        categories = self._api._get(url)
        return [SolutionCategory(**r) for r in categories]

    def get_category(self, category_id):
        url = "solutions/categories/%d" % category_id
        return SolutionCategory(**self._api._get(url))

    def create_category(self, *args, **kwargs):
        url = "solutions/categories"
        return SolutionCategory(**self._api._post(url, data=json.dumps(kwargs)))

    def create_category_translation(self, category_id, lang_code, *args, **kwargs):
        url = "solutions/categories/%d/%s" %(category_id, lang_code)
        return SolutionCategory(**self._api._post(url, data=json.dumps(kwargs)))

    def update_category(self, category_id, *args, **kwargs):
        url = "solutions/categories/%d" % category_id
        return SolutionCategory(**self._api._put(url, data=json.dumps(kwargs)))

    def update_category_translation(self, category_id, lang_code, *args, **kwargs):
        url = "solutions/categories/%d/%s" %(category_id, lang_code)
        return SolutionCategory(**self._api._put(url, data=json.dumps(kwargs)))

    def delete_category(self, category_id):
        url = 'solutions/categories/%s' % category_id
        self._api._delete(url)

    def get_category_translated(self, category_id, lang_code):
        url = "solutions/categories/%d/%s" % (category_id,lang_code)
        return SolutionCategory(**self._api._get(url))


class SolutionFolderAPI(object):
    def __init__(self, api):
        self._api = api

    def list_from_category(self, category_id):
        url = "solutions/categories/%d/folders" % category_id
        folders = self._api._get(url)
        return [SolutionFolder(**r) for r in folders]

    def list_from_category_translated(self, category_id, lang_code):
        url = "solutions/categories/%d/folders/%s" % (category_id, lang_code)
        folders = self._api._get(url)
        return [SolutionFolder(**r) for r in folders]

    def get_folder(self, folder_id):
        url = "solutions/folders/%d" % folder_id
        return SolutionFolder(**self._api._get(url))

    def get_folder_translated(self, folder_id, lang_code):
        url = "solutions/folders/%d/%s" % (folder_id, lang_code)
        return SolutionFolder(**self._api._get(url))

    def create_folder(self, category_id, *args, **kwargs):
        url = "solutions/categories/%s/folders" % category_id
        return SolutionFolder(**self._api._post(url, data=json.dumps(kwargs)))

    def create_folder_translation(self, folder_id, lang_code, *args, **kwargs):
        url = "solutions/folders/%s/%s" % ( folder_id, lang_code)
        return SolutionFolder(**self._api._post(url, data=json.dumps(kwargs)))

    def update_folder(self, folder_id, *args, **kwargs):
        url = "solutions/folders/%s" % (folder_id)
        data = {}
        data.update(kwargs)
        return SolutionFolder(**self._api._put(url, data=json.dumps(data)))

    def update_folder_translation(self, folder_id, lang_code, *args, **kwargs):
        url = "solutions/folders/%s/%s" % (folder_id, lang_code)
        print(url)
        data = {}
        data.update(kwargs)
        return SolutionFolder(**self._api._put(url, data=json.dumps(data)))

    def delete_folder(self, folder_id):
        url = "solutions/folders/%s" % (folder_id)
        self._api._delete(url)


class SolutionArticleAPI(object):
    def __init__(self, api):
        self._api = api

    def get_article(self, article_id):
        url = "solutions/articles/%d" % article_id
        return SolutionArticle(**self._api._get(url))

    def get_article_translated(self, article_id, language_code):
        url = "solutions/articles/%d/%s" % (article_id,language_code)
        return SolutionArticle(**self._api._get(url))

    def list_from_folder(self, id):
        url = "solutions/folders/%d/articles" % id
        articles = self._api._get(url)
        return [SolutionArticle(**a) for a in articles]

    def list_from_folder_translated(self, id, language_code):
        url = "solutions/folders/%d/articles/%s" % (id, language_code)
        articles = self._api._get(url)
        return [SolutionArticle(**a) for a in articles]

    def create_article(self, folder_id, *args, **kwargs):
        url = 'solutions/folders/%s/articles' % folder_id
        return SolutionArticle(**self._api._post(url, data=json.dumps(kwargs)))

    def create_article_translation(self, article_id, lang, *args, **kwargs):
        url = 'solutions/articles/%s/%s' %( article_id, lang )
        return SolutionArticle(**self._api._post(url, data=json.dumps(kwargs)))

    def update_article(self, article_id, *args, **kwargs):
        url = 'solutions/articles/%s' % article_id
        return SolutionArticle(**self._api._put(url, data=json.dumps(kwargs)))

    def update_article_translation(self, article_id, lang, *args, **kwargs):
        url = 'solutions/articles/%s/%s' % ( article_id, lang )
        return SolutionArticle(**self._api._put(url, data=json.dumps(kwargs)))

    def delete_article(self, article_id):
        url = 'solutions/articles/%s' % article_id
        self._api._delete(url)

    def search(self, keyword):
        url = 'search/solutions?term=%s' % keyword
        articles = []
        for r in self._api._get(url):
            articles.append(SolutionArticle(**r))
        return articles

class SolutionAPI(object):
    def __init__(self, api):
        self._api = api
        self.categories = SolutionCategoryAPI(api)
        self.folders = SolutionFolderAPI(api)
        self.articles = SolutionArticleAPI(api)

class API(object):
    def __init__(self, domain, api_key, verify=True, proxies=None):
        """Creates a wrapper to perform API actions.

        Arguments:
          domain:    the Freshdesk domain (not custom). e.g. company.freshdesk.com
          api_key:   the API key

        Instances:
          .tickets:  the Ticket API
        """

        self._api_prefix = "https://{}/api/v2/".format(domain.rstrip("/"))
        self._session = requests.Session()
        self._session.auth = (api_key, "unused_with_api_key")
        self._session.verify = verify
        self._session.proxies = proxies
        self._session.headers = {"Content-Type": "application/json"}

        self.tickets = TicketAPI(self)
        self.comments = CommentAPI(self)
        self.contacts = ContactAPI(self)
        self.companies = CompanyAPI(self)
        self.groups = GroupAPI(self)
        self.customers = CustomerAPI(self)
        self.agents = AgentAPI(self)
        self.roles = RoleAPI(self)
        self.ticket_fields = TicketFieldAPI(self)
        self.time_entries = TimeEntryAPI(self)
        self.solutions = SolutionAPI(self)

        if domain.find("freshdesk.com") < 0:
            raise AttributeError("Freshdesk v2 API works only via Freshdesk" "domains and not via custom CNAMEs")
        self.domain = domain

    def _action(self, req):
        try:
            j = req.json()
        except ValueError:
            j = {}

        error_message = "Freshdesk Request Failed"
        if "errors" in j:
            error_message = "{}: {}".format(j.get("description"), j.get("errors"))
        elif "message" in j:
            error_message = j["message"]

        if req.status_code == 400:
            raise FreshdeskBadRequest(error_message)
        elif req.status_code == 401:
            raise FreshdeskUnauthorized(error_message)
        elif req.status_code == 403:
            raise FreshdeskAccessDenied(error_message)
        elif req.status_code == 404:
            raise FreshdeskNotFound(error_message)
        elif req.status_code == 429:
            raise FreshdeskRateLimited(
                "429 Rate Limit Exceeded: API rate-limit has been reached until {} seconds. See "
                "http://freshdesk.com/api#ratelimit".format(req.headers.get("Retry-After"))
            )
        elif 500 < req.status_code < 600:
            raise FreshdeskServerError("{}: Server Error".format(req.status_code))

        # Catch any other errors
        try:
            req.raise_for_status()
        except HTTPError as e:
            raise FreshdeskError("{}: {}".format(e, j))

        return j

    def _get(self, url, params={}):
        """Wrapper around request.get() to use the API prefix. Returns a JSON response."""
        req = self._session.get(self._api_prefix + url, params=params)
        return self._action(req)

    def _post(self, url, data={}, **kwargs):
        """Wrapper around request.post() to use the API prefix. Returns a JSON response."""
        req = self._session.post(self._api_prefix + url, data=data, **kwargs)
        return self._action(req)

    def _put(self, url, data={}):
        """Wrapper around request.put() to use the API prefix. Returns a JSON response."""
        req = self._session.put(self._api_prefix + url, data=data)
        return self._action(req)

    def _delete(self, url):
        """Wrapper around request.delete() to use the API prefix. Returns a JSON response."""
        req = self._session.delete(self._api_prefix + url)
        print(req)
        return self._action(req)
