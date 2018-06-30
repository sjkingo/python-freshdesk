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

    if version == 1:
        deprecation_message = """
            Freshdesk has deprecated their V1 API from 1st July, 2018.
            For more info, visit https://support.freshdesk.com/support/solutions/articles/231955-important-deprecation-of-api-v1
            
            For more info about freshdesk V2 API, visit https://developers.freshdesk.com/api/
            
            Now python-freshdesk library will by default return V2 API client. You need to migrate your project accordingly.
            
            
        """
        print(deprecation_message)
        version = 2

    if version != 2:
        print("Freshdesk V%d API is not released yet. Returning default V2 API client\n" % version)

    version = 2
    client_class = _VERSIONS[version]
    return client_class(domain, api_key, **kwargs)
