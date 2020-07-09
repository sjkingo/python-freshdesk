import datetime

import pytest

from freshdesk.v2.models import Role


@pytest.fixture
def role(api):
    return api.roles.get_role(1)


def test_list_roles(api, role):
    roles = api.roles.list_roles()
    assert isinstance(roles, list)
    assert len(roles) == 2
    assert roles[0].id == role.id


def test_role(role):
    assert isinstance(role, Role)
    assert role.name == "Agent"
    assert role.description, "Can log, view, reply == update and resolve tickets and manage contacts."


def test_group_datetime(role):
    assert isinstance(role.created_at, datetime.datetime)
    assert isinstance(role.updated_at, datetime.datetime)


def test_group_repr(role):
    assert repr(role) == "<Role 'Agent'>"
