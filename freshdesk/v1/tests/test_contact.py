import datetime

import pytest

from freshdesk.v1.models import Contact, Agent


@pytest.fixture
def contact(api):
    return api.contacts.get_contact(1)


def test_get_contact(contact):
    assert isinstance(contact, Contact)
    assert contact.name == 'Rachel'
    assert contact.email == 'rachel@freshdesk.com'
    assert contact.helpdesk_agent is False
    assert contact.customer_id == 1


def test_list_contacts(api, contact):
    contacts = api.contacts.list_contacts()
    assert isinstance(contacts, list)
    assert len(contacts) == 2
    assert isinstance(contacts[0], Contact)
    assert contacts[0].id == contact.id
    assert contacts[0].email == contact.email
    assert contacts[0].name == contact.name


def test_create_contact(api):
    contact_data = {
        'name': 'Rachel',
        'email': 'rachel@freshdesk.com'
    }
    contact = api.contacts.create_contact(contact_data)
    assert isinstance(contact, Contact)
    assert contact.id == contact.id
    assert contact.email == contact.email
    assert contact.name == contact.name


def test_make_agent(api, contact):
    agent = api.contacts.make_agent(contact.id)
    assert isinstance(agent, Agent)
    assert agent.available is True
    assert agent.occasional is False
    assert agent.id == 1
    assert agent.user_id == contact.id
    assert agent.user['email'] == contact.email
    assert agent.user['name'] == contact.name


def test_delete_contact(api):
    assert api.contacts.delete_contact(1) is None


def test_contact_datetime(contact):
    assert isinstance(contact.created_at, datetime.datetime)
    assert isinstance(contact.updated_at, datetime.datetime)


def test_contact_str(contact):
    assert str(contact) == 'Rachel'


def test_contact_repr(contact):
    assert repr(contact) == '<Contact \'Rachel\'>'
