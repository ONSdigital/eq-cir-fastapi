from tests.test_config.endpoints import EndpointConfig


class EndpointsLoader:
    def __init__(self, endpoints: dict[str, EndpointConfig]):
        self.endpoints = endpoints

    def get_url(self, key: str):
        return self.endpoints.get(key)["url"]