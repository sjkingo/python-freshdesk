from freshdesk.v1 import api as v1_api
from freshdesk.v2 import api as v2_api


_VERSIONS = {1: v1_api.API,
             2: v2_api.API}


class FreshdeskAPI(object):
    def __init__(self, domain, api_key, version=2):
        """Creates a wrapper to perform API actions.

        Arguments:
          domain:    the Freshdesk domain (not custom). e.g. company.freshdesk.com
          api_key:   the API key
          verions:   version of the API to use (v1 default)
        """


def API(domain, api_key, version=1, **kwargs):

    # trim the v from a 'v1' or similar
    try:
        version = version.lstrip('v')
    except AttributeError:
        pass

    client_class = _VERSIONS[version]
    return client_class(domain, api_key, **kwargs)
