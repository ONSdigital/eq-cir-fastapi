from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient

from app.config import Settings
from app.routers.status_router import app

client = TestClient(app)
settings = Settings()

class TestDeploymentStatus:
    base_url = "/status"

    def test_endpoint_returns_200_if_deployment_successful(self):
        """
        Endpoint should return `HTTP_200_OK` if the deployment is successful
        """
        response = client.get(self.base_url)
        assert response.status_code == status.HTTP_200_OK

    @patch("app.status_router.settings")
    def test_endpoint_returns_right_message_if_deployment_successful(self, mocked_settings):
        """
        Endpoint should return the right response if the deployment is successful
        """
        # mocked `settings` to set the CIR_APPLICATION_VERSION to dev-048783a4
        mocked_settings.CIR_APPLICATION_VERSION = "dev-048783a4"
        response = client.get(self.base_url)
        expected_message = '{"version":"dev-048783a4","status":"OK"}'
        assert expected_message in response.content.decode("utf-8")

    @patch("app.status_router.settings")
    def test_endpoint_returns_500_if_deployment_successful(self, mocked_settings):
        """
        Endpoint should return `HTTP_500_INTERNAL_SERVER_ERROR` if the env var is
        None due to a unsuccesful deployment
        """
        # mocked `settings` to set the CIR_APPLICATION_VERSION to None

        mocked_settings.CIR_APPLICATION_VERSION = None
        response = client.get(self.base_url)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        expected_message = '{"message":"Internal server error","status":"error"}'
        assert expected_message in response.content.decode("utf-8")
