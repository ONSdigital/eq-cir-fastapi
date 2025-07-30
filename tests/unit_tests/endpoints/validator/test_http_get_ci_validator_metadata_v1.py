from unittest.mock import patch

from tests.test_data.ci_test_data import mock_ci_validator_metadata_list
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
test_500_client = TestClient(app, raise_server_exceptions=False)


class TestHttpGetCiValidatorMetadataV1:

    url = "/v1/ci_validator_metadata"

    @patch("app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.get_ci_validator_metadata_collection")
    def test_endpoint_returns_200(self, mock_get_ci_validator_metadata_collection):
        """
        Tests the `http_get_ci_validator_metadata` endpoint returns 200 with expected data.
        """
        mock_get_ci_validator_metadata_collection.return_value = mock_ci_validator_metadata_list

        response = client.get(self.url)

        assert response.status_code == 200
        for i in range(len(response.json())):
            assert response.json()[i] == mock_ci_validator_metadata_list[i].model_dump()

    @patch("app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.get_ci_validator_metadata_collection")
    def test_endpoint_returns_404_if_validator_metadata_not_found(self, mock_get_ci_validator_metadata_collection):
        """
        Tests the `http_get_ci_validator_metadata` endpoint returns 404 when no metadata is found.
        """
        mock_get_ci_validator_metadata_collection.return_value = []

        response = client.get(self.url)

        assert response.status_code == 404
        assert response.json()["message"] == "No CI validator metadata found"

    @patch("app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.get_ci_validator_metadata_collection")
    def test_endpoint_returns_500_when_repository_fails(self, mock_get_ci_validator_metadata_collection):
        """
        Tests the `http_get_ci_validator_metadata` endpoint returns 500 when the repository fails.
        """
        mock_get_ci_validator_metadata_collection.side_effect = Exception("Repository error")

        response = test_500_client.get(self.url)

        assert response.status_code == 500
        assert response.json()["message"] == "Unable to process request"
