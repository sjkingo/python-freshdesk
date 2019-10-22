import pytest

from freshdesk.v2.models import Comment


@pytest.fixture
def comments(api):
    return api.comments.list_comments(1)


def test_comments_list(comments):
    assert isinstance(comments, list)
    assert len(comments) == 2
    assert isinstance(comments[0], Comment)


def test_comment_str(comments):
    assert str(comments[0]) == 'This is a private note'


def test_comment_repr(comments):
    assert repr(comments[0]) == '<Comment for Ticket #1>'


def test_create_note(api):
    comment = api.comments.create_note(1, 'This is a private note')
    assert isinstance(comment, Comment)
    assert comment.body_text == 'This is a private note'
    assert comment.source == 'note'


def test_create_reply(api):
    comment = api.comments.create_reply(1, 'This is a reply')
    assert isinstance(comment, Comment)
    assert comment.body_text == 'This is a reply'
    assert comment.source == 'reply'
