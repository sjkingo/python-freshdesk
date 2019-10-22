import pytest

from freshdesk.v1.models import TimeEntry


@pytest.fixture
def timesheet(api):
    return api.timesheets.get_timesheet_by_ticket(1)


def test_timesheet(timesheet):
    assert isinstance(timesheet, type([]))
    assert len(timesheet) == 3
    assert isinstance(timesheet[1], TimeEntry)
    assert timesheet[1].id == 6000041896
    assert timesheet[1].note == "Foo"
    assert timesheet[1].timespent == "0.33"


def test_timesheet_str(timesheet):
    assert str(timesheet[1]) == "6000041896"


def test_timesheet_repr(timesheet):
    assert repr(timesheet[1]) == '<Timesheet Entry 6000041896>'


def test_get_all_timesheets(api):
    timesheet = api.timesheets.get_all_timesheets()
    test_timesheet(timesheet)
    timesheet = api.timesheets.get_all_timesheets(filter_name="agent_id", filter_value="5004272350")
    test_timesheet(timesheet)
