import pytest
import responses

from freshdesk.v1.api import API
from freshdesk.v1.tests.conftest import DOMAIN


def test_api_prefix():
    api = API("test_domain", "test_key")
    assert api._api_prefix == "https://test_domain/"
    api = API("test_domain/", "test_key")
    assert api._api_prefix == "https://test_domain/"


@responses.activate
def test_403_error():
    responses.add(responses.GET, "https://{}/helpdesk/tickets/1.json".format(DOMAIN), status=403)

    api = API(DOMAIN, "invalid_api_key")
    from requests.exceptions import HTTPError

    with pytest.raises(HTTPError):
        api.tickets.get_ticket(1)


@responses.activate
def test_404_error():
    DOMAIN_404 = "google.com"
    responses.add(responses.GET, "https://{}/helpdesk/tickets/1.json".format(DOMAIN_404), status=404)

    api = API(DOMAIN_404, "invalid_api_key")
    from requests.exceptions import HTTPError

    with pytest.raises(HTTPError):
        api.tickets.get_ticket(1)
