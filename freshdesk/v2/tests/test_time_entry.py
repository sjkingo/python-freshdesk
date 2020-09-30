import pytest

from freshdesk.v2.models import TimeEntry


@pytest.fixture
def time_entries_1(api):
    return api.time_entries.list_time_entries(1)

@pytest.fixture
def time_entries_all(api):
    return api.time_entries.list_time_entries()


def test_time_entries_1_list(time_entries_1):
    assert isinstance(time_entries_1, list)
    assert len(time_entries_1) == 3
    assert isinstance(time_entries_1[0], TimeEntry)


def test_time_entries_all_list(time_entries_all):
    assert isinstance(time_entries_all, list)
    assert len(time_entries_all) == 3
    assert isinstance(time_entries_all[0], TimeEntry)


def test_time_entries_1_str(time_entries_1):
    assert str(time_entries_1[0]) == "This is test time entry (00:10)"


def test_time_entries_all_str(time_entries_all):
    assert str(time_entries_all[0]) == "This is the first entry (00:15)"


def test_time_entries_1_repr(time_entries_1):
    assert repr(time_entries_1[0]) == "<Timesheet entry for Ticket #521>"


def test_time_entries_all_repr(time_entries_all):
    assert repr(time_entries_all[0]) == "<Timesheet entry for Ticket #1>"

