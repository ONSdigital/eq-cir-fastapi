from fastapi import status

from app.config import Settings
from tests.integration_tests.utils import make_iap_request

settings = Settings()


class TestHttpGetDeploymentStatus:
    """Tests for the `http_get_status` endpoint."""

    deployment_status_url = "/status"

    def test_endpoint_returns_200_success_if_env_var_found(self):
        """Endpoint should return `HTTP_200_OK` if the deployment is successful
        """
        status_response = make_iap_request("GET", self.deployment_status_url)
        assert status_response.status_code == status.HTTP_200_OK

    def test_endpoint_returns_right_response_if_deployment_successful(self):
        """Endpoint should return return the right response if the deployment is successful
        """
        # mocked `get_ci_schema_v2` to return valid ci metadata

        status_response = make_iap_request("GET", self.deployment_status_url)
        status_response = status_response.json()
        status_response["version"] == settings.CIR_APPLICATION_VERSION
        status_response["status"] == "Ok"

    def test_endpoint_returns_unauthorized_request(self):
        """Endpoint should return a 401 unauthorized error if the endpoint is requested with an unauthorized token.
        """
        status_response = make_iap_request("GET", self.deployment_status_url, unauthenticated=True)
        assert status_response.status_code == status.HTTP_401_UNAUTHORIZED
