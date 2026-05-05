import os

from tests.test_config.endpoints import ENDPOINTS_DEPRECATED, EndpointConfig


class EndpointsLoader:
    def __init__(self, endpoints: dict[str, EndpointConfig], ignore_deprecated: bool = False):
        """
        Load the endpoints config

        :param endpoints: dictionary containing the endpoint and the url and method for that endpoint
        :param ignore_deprecated: boolean flag to ignore environment variable to switch to deprecated endpoints
        """

        # Temporary logic to load deprecated endpoints if `ENDPOINTS_DEPRECATED` environment variable is set to "true".
        # This allows us to run tests against both the new and deprecated endpoints without needing to change the code in multiple places.
        # This logic can be removed once the deprecated endpoints are removed.
        if os.environ.get("ENDPOINTS_DEPRECATED") == "true" and ignore_deprecated is False:
            self.endpoints = ENDPOINTS_DEPRECATED
        else:
            self.endpoints = endpoints

    def get_url(self, key: str):
        return self.endpoints.get(key)["url"]
