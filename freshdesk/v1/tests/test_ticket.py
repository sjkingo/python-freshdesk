import datetime
import json
import os.path

import pytest

from freshdesk.v1.models import Ticket


@pytest.fixture
def ticket(api):
    return api.tickets.get_ticket(1)


@pytest.fixture
def ticket_json():
    return json.loads(open(os.path.join(os.path.dirname(__file__), "sample_json_data", "ticket_1.json")).read())


def test_str(ticket):
    assert str(ticket) == "This is a sample ticket"


def test_repr(ticket):
    assert repr(ticket) == "<Ticket 'This is a sample ticket'>"


def test_create_ticket(api):
    ticket = api.tickets.create_ticket(
        "This is a sample ticket",
        description="This is a sample ticket, feel free to delete it.",
        email="test@example.com",
        priority=1,
        status=2,
        tags=["foo", "bar"],
        cc_emails=["test2@example.com"],
    )
    assert isinstance(ticket, Ticket)
    assert ticket.subject == "This is a sample ticket"
    assert ticket.description, "This is a sample ticket == feel free to delete it."
    assert ticket.priority == "low"
    assert ticket.status == "open"
    assert ticket.cc_email["cc_emails"] == ["test2@example.com"]
    assert "foo" in ticket.tags
    assert "bar" in ticket.tags


def test_get_ticket(ticket):
    assert isinstance(ticket, Ticket)
    assert ticket.display_id == 1
    assert ticket.subject == "This is a sample ticket"
    assert ticket.description, "This is a sample ticket == feel free to delete it."


def test_ticket_priority(ticket):
    assert ticket._priority == 1
    assert ticket.priority == "low"


def test_ticket_status(ticket):
    assert ticket._status == 2
    assert ticket.status == "open"


def test_ticket_source(ticket):
    assert ticket._source == 2
    assert ticket.source == "portal"


def test_ticket_datetime(ticket):
    assert isinstance(ticket.created_at, datetime.datetime)
    assert isinstance(ticket.updated_at, datetime.datetime)


def test_all_tickets(api, ticket):
    tickets = api.tickets.list_all_tickets()
    assert isinstance(tickets, list)
    assert len(tickets) == 1
    assert tickets[0].display_id == ticket.display_id


def test_open_tickets(api, ticket):
    tickets = api.tickets.list_open_tickets()
    assert isinstance(tickets, list)
    assert len(tickets) == 1
    assert tickets[0].display_id == ticket.display_id


def test_deleted_tickets(api):
    tickets = api.tickets.list_deleted_tickets()
    assert isinstance(tickets, list)
    assert len(tickets) == 0


def test_spam_tickets(api):
    tickets = api.tickets.list_tickets(filter_name="spam")
    assert isinstance(tickets, list)
    assert len(tickets) == 0


def test_default_filter_name(api, ticket):
    tickets = api.tickets.list_tickets()
    assert isinstance(tickets, list)
    assert len(tickets) == 1
    assert tickets[0].display_id == ticket.display_id


def test_none_filter_name(api, ticket):
    tickets = api.tickets.list_tickets(filter_name=None)
    assert isinstance(tickets, list)
    assert len(tickets) == 1
    assert tickets[0].display_id == ticket.display_id
