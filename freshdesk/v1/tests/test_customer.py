import datetime

import pytest

from freshdesk.v1.models import Customer


@pytest.fixture
def customer(api):
    return api.customers.get_customer(1)


@pytest.fixture
def contact(api):
    return api.contacts.get_contact(1)


def test_customer(customer):
    assert isinstance(customer, Customer)
    assert customer.name == "ACME Corp."
    assert customer.domains == "acme.com"
    assert customer.cf_custom_key == "custom_value"


def test_contact_datetime(customer):
    assert isinstance(customer.created_at, datetime.datetime)
    assert isinstance(customer.updated_at, datetime.datetime)


def test_contact_str(customer):
    assert str(customer) == "ACME Corp."


def test_contact_repr(customer):
    assert repr(customer) == "<Customer 'ACME Corp.'>"


def test_get_customer_from_contact(api, contact):
    customer = api.customers.get_customer_from_contact(contact)
    test_customer(customer)
