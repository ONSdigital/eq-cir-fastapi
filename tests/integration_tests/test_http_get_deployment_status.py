from fastapi import status

from app.config import Settings
from tests.integration_tests.utils import make_iap_request

settings = Settings()


class TestHttpGetDeploymentStatus:
    """Tests for the `http_post_ci_v1` endpoint."""

    deployment_status_url = "/status"

    def test_endpoint_returns_200_success_if_env_var_found(self):
        """
        This function deletes the test CI with survey_id:3456 at the end of each integration test to ensure it
        is not reflected in the firestore and schemas.
        """
        status_response = make_iap_request("GET", self.deployment_status_url)
        assert status_response.status_code == status.HTTP_200_OK

    def test_endpoint_returns_right_message_if_deployment_successful(self):
        """
        Endpoint should return `HTTP_200_OK` if status is updated to published
        """
        # mocked `get_ci_schema_v2` to return valid ci metadata

        status_response = make_iap_request("GET", self.deployment_status_url)
        status_response = status_response.json()
        status_response["version"] == settings.CIR_APPLICATION_VERSION
        status_response["status"] == "Ok"
