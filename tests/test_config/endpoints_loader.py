import os

from tests.test_config.endpoints import EndpointConfig


class EndpointsLoader:
    def __init__(self, endpoints: dict[str, EndpointConfig]):
        # Temporary logic to load deprecated endpoints if `ENDPOINTS_DEPRECATED` environment variable is set to "true".
        # This allows us to run tests against both the new and deprecated endpoints without needing to change the code in multiple places.
        # This logic can be removed once the deprecated endpoints are removed.
        if os.environ.get("ENDPOINTS_DEPRECATED") == "true":
            from tests.test_config.endpoints import ENDPOINTS_DEPRECATED

            self.endpoints = ENDPOINTS_DEPRECATED
        else:
            self.endpoints = endpoints

    def get_url(self, key: str):
        return self.endpoints.get(key)["url"]