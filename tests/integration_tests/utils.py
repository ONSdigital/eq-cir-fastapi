import requests
from google.auth.transport.requests import Request
from google.oauth2 import id_token

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
    else:
        # Set Headers using fetched id token. Requires valid credentials file at path specified by the
        # `GOOGLE_APPLICATION_CREDENTIALS` env var. See README.md for more details
        auth_token = id_token.fetch_id_token(Request(), audience=settings.OAUTH_CLIENT_ID)

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }
    url = f"{settings.URL_SCHEME}://{settings.DEFAULT_HOSTNAME}{path}"

    # Fetch the Identity-Aware Proxy-protected URL, including an
    # Authorization header containing "Bearer " followed by a
    # Google-issued OpenID Connect token for the service account.
    return requests.request(method, url, headers=headers, **kwargs)
