import uuid
from urllib.parse import urlencode

import requests
from sds_common.services.http_service import HttpService

from app.config import Settings

settings = Settings()


def make_iap_request(method, path, **kwargs):
    """
    Makes a request to an application protected by Identity-Aware Proxy.

    Args:
        method: The request method to use
            ('GET', 'OPTIONS', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE')
        path: The Identity-Aware Proxy-protected path to fetch.
        **kwargs: Any of the parameters defined for the request function:
            https://github.com/requests/requests/blob/master/requests/api.py
            If no timeout is provided, it is set to 90 by default.

    Returns:
        The page body, or raises an exception if the page couldn't be retrieved.
    """

    # Set the default timeout, if missing
    if "timeout" not in kwargs:
        kwargs["timeout"] = 60

    # If unauthenticated request, pop out from kwargs so we don't pass to `requests.request`
    if "unauthenticated" in kwargs:
        kwargs.pop("unauthenticated")
        auth_token = "bad-request-key"
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }
    elif settings.CONF == 'local-int-tests':
        # For local docker integration tests, we bypass the token
        auth_token = 'default'
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }
    elif settings.CONF == 'sandbox-int-tests':
        headers = HttpService.generate_authentication_headers_by_impersonation()
    else:
        headers = HttpService.generate_authentication_headers()

    url = f"{settings.URL_SCHEME}://{settings.DEFAULT_HOSTNAME}{path}"

    # Fetch the Identity-Aware Proxy-protected URL, including an
    # Authorization header containing "Bearer " followed by a
    # Google-issued OpenID Connect token for the service account.
    return requests.request(method, url, headers=headers, **kwargs)


def create_post_params(number_of_items: int, validator_version = "0.0.1"):
    list_of_params = []
    for _ in range(number_of_items):
        params = {
            "guid": str(uuid.uuid4()),
            "validator_version": validator_version
        }
        list_of_params.append(urlencode(params))
    return list_of_params

