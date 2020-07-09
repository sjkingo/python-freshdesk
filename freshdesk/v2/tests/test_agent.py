import datetime
import json
import os.path

import pytest

from freshdesk.v2.models import Agent


@pytest.fixture
def agent(api):
    return api.agents.get_agent(1)


@pytest.fixture
def agent_json():
    return json.loads(open(os.path.join(os.path.dirname(__file__), "sample_json_data", "agent_1.json")).read())


def test_str(agent):
    assert str(agent) == "Rachel"


def test_repr(agent):
    assert repr(agent) == "<Agent #1 'Rachel'>"


def test_get_agent(agent):
    assert isinstance(agent, Agent)
    assert agent.id == 1
    assert agent.contact["name"] == "Rachel"
    assert agent.contact["email"] == "rachel@freshdesk.com"
    assert agent.contact["mobile"] == 1234
    assert agent.contact["phone"] == 5678
    assert agent.occasional is False


def test_update_agent(api):
    values = {"occasional": True, "contact": {"name": "Updated Name"}}
    agent = api.agents.update_agent(1, **values)

    assert agent.occasional is True
    assert agent.contact["name"] == "Updated Name"


def test_delete_agent(api):
    assert api.agents.delete_agent(1) is None


def test_agent_name(agent):
    assert agent.contact["name"] == "Rachel"


def test_agent_mobile(agent):
    assert agent.contact["mobile"] == 1234


def test_agent_state(agent):
    assert agent.available is True
    assert agent.occasional is False


def test_agent_datetime(agent):
    assert isinstance(agent.created_at, datetime.datetime)
    assert isinstance(agent.updated_at, datetime.datetime)


def test_none_filter_name(api, agent):
    agents = api.agents.list_agents()
    assert isinstance(agents, list)
    assert len(agents) == 2
    assert agents[0].id == agent.id
