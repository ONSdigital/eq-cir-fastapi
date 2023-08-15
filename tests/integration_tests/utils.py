import re
from urllib.parse import urlencode

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


def post_ci_v1(payload):
    """Creates schema for testing purposes

    Args:
        payload (json): json to be sent to API

    Returns:
        obj: response object
    """
    return make_iap_request("POST", "/v1/publish_collection_instrument", json=payload)


def put_status_v1(guid: str):
    """
    Updates schema for testing purposes
    Args:
        guid: to be passed as part of a querystring to URL making PUT request
    Returns:
        obj: `requests.response` object
    """
    querystring = urlencode({"guid": guid})

    return make_iap_request("PUT", f"/v1/update_status?{querystring}")


def get_ci_metadata_v1(survey_id: str, form_type: str, language: str):
    """
    Gets schema for testing purposes
    Args:
        form_type: to be passed as part of a querystring to URL making GET request
        language: to be passed as part of a querystring to URL making GET request
        survey_id: to be passed as part of a querystring to URL making GET request
    Returns:
        obj: `requests.response` object
    """
    querystring = urlencode({"form_type": form_type, "language": language, "survey_id": survey_id})

    return make_iap_request("GET", f"/v1/ci_metadata?{querystring}")


def delete_docs(survey_id: str):
    """
    Deletes firestore documents
    Args:
        survey_id: to be passed as part of a querystring to URL making DELETE request
    Returns:
        obj: `requests.response` object
    """
    querystring = urlencode({"survey_id": survey_id})

    return make_iap_request("DELETE", f"/v1/dev/teardown?{querystring}")


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


def get_ci_schema_v2(guid: str):
    """
    Gets CI schema using input `guid`
    Args:
        guid: to be passed as part of a querystring to URL making DELETE request
    Returns:
        obj: `requests.response` object
    """

    querystring = urlencode({"guid": guid})

    return make_iap_request("GET", f"/v2/retrieve_collection_instrument?{querystring}")


def get_ci_metadata_v2(payload=None):
    """
    Makes `get` request to the `/v2/ci_metadata` endpoint and return the response.
    If input `payload` is not `None`, make request with the input `payload`
    dictionary encoded as querystring parameters.
    """

    request_path = "/v2/ci_metadata"

    # If valid payload, append querystring to `request_path` before making request
    if payload:
        querystring = urlencode(payload)
        request_path += f"?{querystring}"

    return make_iap_request("GET", request_path)
