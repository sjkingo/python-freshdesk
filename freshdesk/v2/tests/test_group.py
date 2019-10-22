import datetime

import pytest

from freshdesk.v2.models import Group


@pytest.fixture
def group(api):
    return api.groups.get_group(1)


def test_list_groups(api, group):
    groups = api.groups.list_groups()
    assert isinstance(groups, list)
    assert len(groups) == 2
    assert groups[0].id == group.id


def test_group(group):
    assert isinstance(group, Group)
    assert group.name == 'Entertainers'
    assert group.description == 'Singers dancers and stand up comedians'


def test_group_datetime(group):
    assert isinstance(group.created_at, datetime.datetime)
    assert isinstance(group.updated_at, datetime.datetime)


def test_group_str(group):
    assert str(group) == 'Entertainers'


def test_group_repr(group):
    assert repr(group) == '<Group \'Entertainers\'>'
