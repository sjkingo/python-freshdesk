import pytest

from freshdesk.v1.models import Comment


@pytest.fixture
def ticket(api):
    return api.tickets.get_ticket(1)


def test_comments_list(ticket):
    assert isinstance(ticket.comments, list)
    assert len(ticket.comments) == 1
    assert isinstance(ticket.comments[0], Comment)


def test_comment_str(ticket):
    assert str(ticket.comments[0]) == 'This is a reply.'


def test_comment_repr(ticket):
    assert repr(ticket.comments[0]) == '<Comment for <Ticket \'This is a sample ticket\'>>'
