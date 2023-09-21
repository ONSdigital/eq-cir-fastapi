import re

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

    # Set Headers using fetched id token. Requires valid credentials file at path specified by the
    # `GOOGLE_APPLICATION_CREDENTIALS` env var. See README.md for more details
    auth_token = id_token.fetch_id_token(Request(), audience=settings.OAUTH_CLIENT_ID)

    headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    url = f"{settings.URL_SCHEME}://{settings.DEFAULT_HOSTNAME}{path}"

    # Fetch the Identity-Aware Proxy-protected URL, including an
    # Authorization header containing "Bearer " followed by a
    # Google-issued OpenID Connect token for the service account.
    return requests.request(method, url, headers=headers, **kwargs)


def is_valid_datetime(dt_str: str):
    """
    Validates iso8601 string - ISO 8601 represents date and time by starting with the year,
    followed by the month, the day, the hour, the minutes, seconds and milliseconds.
    Args:
        dt_str: iso 8601 string

    Returns:
        Bool
    """

    datetime_regex = (
        r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])"
        r"T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]"
        r"|[01][0-9]):[0-5][0-9])?$"
    )
    return re.match(datetime_regex, dt_str)
