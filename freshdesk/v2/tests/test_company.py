import datetime
import pytest

from freshdesk.v2.models import Company


@pytest.fixture
def company(api):
    return api.companies.get_company(1)


def test_get_company(company):
    assert isinstance(company, Company)
    assert company.id == 1
    assert company.name == "Super Nova"
    assert company.description == "Space Shuttle Manufacturing"
    assert company.domains == ["supernova", "nova", "super"]
    assert company.industry is None
    assert company.custom_fields.get("website") == "https://www.supernova.org"


def test_contact_datetime(company):
    assert isinstance(company.created_at, datetime.datetime)
    assert isinstance(company.updated_at, datetime.datetime)


def test_company_str(company):
    assert str(company) == "Super Nova"


def test_company_repr(company):
    assert repr(company) == "<Company 'Super Nova'>"


def test_list_companies(api, company):
    companies = api.companies.list_companies()
    assert isinstance(companies, list)
    assert isinstance(companies[0], Company)
    assert len(companies) == 2
    assert companies[0].__dict__ == company.__dict__
