import pytest
import responses

from freshdesk.v2.api import API
from freshdesk.v2.errors import (
    FreshdeskBadRequest, FreshdeskAccessDenied, FreshdeskNotFound, FreshdeskError,
    FreshdeskRateLimited,
    FreshdeskServerError,
)
from freshdesk.v2.tests.conftest import DOMAIN


def test_custom_cname():
    with pytest.raises(AttributeError):
        API('custom_cname_domain', 'invalid_api_key')


def test_api_prefix():
    api = API('test_domain.freshdesk.com', 'test_key')
    assert api._api_prefix == 'https://test_domain.freshdesk.com/api/v2/'
    api = API('test_domain.freshdesk.com/', 'test_key')
    assert api._api_prefix == 'https://test_domain.freshdesk.com/api/v2/'


@responses.activate
@pytest.mark.parametrize(
    ('status_code', 'exception'),
    [(400, FreshdeskBadRequest), (403, FreshdeskAccessDenied), (404, FreshdeskNotFound),
     (418, FreshdeskError), (429, FreshdeskRateLimited), (502, FreshdeskServerError)]
)
def test_errors(status_code, exception):
    responses.add(responses.GET,
                  'https://{}/api/v2/tickets/1'.format(DOMAIN),
                  status=status_code)

    api = API('pythonfreshdesk.freshdesk.com', 'test_key')
    with pytest.raises(exception):
        api.tickets.get_ticket(1)
