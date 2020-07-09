import datetime
import json
import os.path
from mock import patch, ANY

import pytest

from freshdesk.v2.models import Ticket


@pytest.fixture
def ticket(api):
    return api.tickets.get_ticket(1)


@pytest.fixture
def ticket_json():
    return json.loads(open(os.path.join(os.path.dirname(__file__), "sample_json_data", "ticket_1.json")).read())


@pytest.fixture
def outbound_email_json(api):
    return json.loads(open(os.path.join(os.path.dirname(__file__), "sample_json_data", "outbound_email_1.json")).read())


def test_str(ticket):
    assert str(ticket) == "This is a sample ticket"


def test_repr(ticket):
    assert repr(ticket) == "<Ticket 'This is a sample ticket' #1>"


def test_get_ticket(ticket):
    assert isinstance(ticket, Ticket)
    assert ticket.id == 1
    assert ticket.subject == "This is a sample ticket"
    assert ticket.description_text, "This is a sample ticket, feel free to delete it."
    assert ticket.cc_emails == ["test2@example.com"]
    assert "foo" in ticket.tags
    assert "bar" in ticket.tags


def test_create_ticket(api):
    ticket = api.tickets.create_ticket(
        "This is a sample ticket",
        description="This is a sample ticket, feel free to delete it.",
        email="test@example.com",
        priority=1,
        status=2,
        tags=["foo", "bar"],
        cc_emails=["test2@example.com", "test3@example.com"],
        custom_fields={"power": 11, "importance": "very"},
    )
    assert isinstance(ticket, Ticket)
    assert ticket.subject == "This is a sample ticket"
    assert ticket.description_text, "This is a sample ticket, feel free to delete it."
    assert ticket.priority == "low"
    assert ticket.status == "open"
    assert ticket.cc_emails == ["test2@example.com"]
    assert "foo" in ticket.tags
    assert "bar" in ticket.tags


def test_create_ticket_with_attachments(api):
    attachment_path = os.path.join(os.path.dirname(__file__), "sample_json_data", "attachment.txt")
    with patch.object(api, "_post", wraps=api._post) as post_mock:
        ticket = api.tickets.create_ticket(
            "This is a sample ticket with an attachment",
            description="This is a sample ticket, feel free to delete it.",
            email="test@example.com",
            priority=1,
            status=2,
            cc_emails=["test2@example.com", "test3@example.com"],
            custom_fields={"power": 11, "importance": "very"},
            attachments=(attachment_path,),
        )

    post_mock.assert_called_once_with(
        "tickets",
        data={
            "subject": "This is a sample ticket with an attachment",
            "status": 2,
            "priority": 1,
            "description": "This is a sample ticket, feel free to delete it.",
            "email": "test@example.com",
            # List argument names should be sent as arrays, otherwise it's not deserialized correctly.
            "cc_emails[]": ["test2@example.com", "test3@example.com"],
            # Dict arguments must unrolled into indexed arrays to work properly with the form-data encoding.
            "custom_fields[power]": 11,
            "custom_fields[importance]": "very",
        },
        files=[("attachments[]", ("attachment.txt", ANY, None))],
        # Content-type should be unset so that `requests` uses "multipart/form-data" instead of application/json.
        headers={"Content-Type": None},
    )

    assert isinstance(ticket, Ticket)
    assert ticket.subject == "This is a sample ticket"
    assert ticket.description_text, "This is a sample ticket, feel free to delete it."
    assert ticket.priority == "low"
    assert ticket.status == "open"
    assert ticket.cc_emails == ["test2@example.com"]
    assert ticket.attachments[0]["name"] == "attachment.txt"
    assert "foo" in ticket.tags
    assert "bar" in ticket.tags


def test_create_outbound_email(api, outbound_email_json):
    j = outbound_email_json.copy()
    email = "test@example.com"
    subject = "This is a sample outbound email"
    description = "This is a sample outbound email, feel free to delete it."
    email_config_id = 5000054536
    values = {"status": 5, "priority": 1, "tags": ["foo", "bar"], "cc_emails": ["test2@example.com"]}

    email = api.tickets.create_outbound_email(subject, description, email, email_config_id, **values)

    assert email.description_text == j["description_text"]
    assert email._priority == j["priority"]
    assert email._status == j["status"]
    assert email.cc_emails == j["cc_emails"]
    assert "foo" in email.tags
    assert "bar" in email.tags


def test_update_ticket(api, ticket_json):
    j = ticket_json.copy()
    values = {"subject": "Test subject update", "priority": 3, "status": 4, "tags": ["hello", "world"]}
    j.update(values)

    ticket = api.tickets.update_ticket(j["id"], **values)
    assert ticket.subject == "Test subject update"
    assert ticket.status == "resolved"
    assert ticket.priority == "high"
    assert "hello" in ticket.tags
    assert "world" in ticket.tags


def test_delete_ticket(api):
    assert api.tickets.delete_ticket(1) is None


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


def test_new_and_my_open_tickets(api, ticket):
    tickets = api.tickets.list_new_and_my_open_tickets()
    assert isinstance(tickets, list)
    assert len(tickets) == 1
    assert tickets[0].id == ticket.id


def test_deleted_tickets(api):
    tickets = api.tickets.list_deleted_tickets()
    assert isinstance(tickets, list)
    assert len(tickets) == 1


def test_watched_tickets(api, ticket):
    tickets = api.tickets.list_watched_tickets()
    assert isinstance(tickets, list)
    assert len(tickets) == 1
    assert tickets[0].id == ticket.id


def test_spam_tickets(api):
    tickets = api.tickets.list_tickets(filter_name="spam")
    assert isinstance(tickets, list)
    assert len(tickets) == 1


def test_default_filter_name(api, ticket):
    tickets = api.tickets.list_tickets()
    assert isinstance(tickets, list)
    assert len(tickets) == 1
    assert tickets[0].id == ticket.id


def test_none_filter_name(api, ticket):
    tickets = api.tickets.list_tickets(filter_name=None)
    assert isinstance(tickets, list)
    assert len(tickets) == 1
    assert tickets[0].id == ticket.id


def test_filter_query(api, ticket):
    tickets = api.tickets.filter_tickets(query="tag:'mytag'")
    assert isinstance(tickets, list)
    assert len(tickets) == 2
    assert "mytag" in tickets[0].tags
