import datetime

import pytest

from freshdesk.v2.models import Contact, Agent


@pytest.fixture
def contact(api):
    return api.contacts.get_contact(1)


def test_get_contact(contact):
    assert isinstance(contact, Contact)
    assert contact.name == "Rachel"
    assert contact.email == "rachel@freshdesk.com"
    assert contact.helpdesk_agent is False
    assert contact.customer_id == 1


def test_list_contact(api, contact):
    contacts = api.contacts.list_contacts()
    assert isinstance(contacts, list)
    assert isinstance(contacts[0], Contact)
    assert len(contacts) == 2
    assert contacts[0].__dict__ == contact.__dict__


def test_create_contact(api):
    contact_data = {"name": "Rachel", "email": "rachel@freshdesk.com"}
    contact = api.contacts.create_contact(contact_data)
    assert isinstance(contact, Contact)
    assert contact.email == contact.email
    assert contact.name == contact.name


def test_filter_query(api):
    contacts = api.contacts.filter_contacts(query="time_zone:Brisbane")
    assert isinstance(contacts, list)
    assert isinstance(contacts[0], Contact)
    assert len(contacts) == 2
    assert contacts[0].name == "Rachel"


def test_update_contact(api):
    contact_data = {"name": "New Name"}
    contact = api.contacts.update_contact(1, **contact_data)
    assert isinstance(contact, Contact)
    assert contact.name == "New Name"


def test_soft_delete_contact(api):
    assert api.contacts.soft_delete_contact(1) is None


def test_permanently_delete_contact(api):
    assert api.contacts.permanently_delete_contact(1) is None


def test_restore_contact(api):
    api.contacts.restore_contact(1)
    contact = api.contacts.get_contact(1)
    assert isinstance(contact, Contact)
    assert contact.deleted is False


def test_make_agent(api, contact):
    agent = api.contacts.make_agent(contact.id)
    assert isinstance(agent, Agent)
    assert agent.available is True
    assert agent.occasional is False
    assert agent.contact["email"] == contact.email
    assert agent.contact["name"] == contact.name


def test_contact_datetime(contact):
    assert isinstance(contact.created_at, datetime.datetime)
    assert isinstance(contact.updated_at, datetime.datetime)


def test_contact_str(contact):
    assert str(contact) == "Rachel"


def test_contact_repr(contact):
    assert repr(contact) == "<Contact 'Rachel'>"
