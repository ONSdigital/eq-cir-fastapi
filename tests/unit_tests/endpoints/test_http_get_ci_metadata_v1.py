from unittest.mock import patch
from urllib.parse import urlencode

from fastapi import status
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app
from app.models.requests import GetCiMetadataV1Params
from app.repositories.firebase.ci_firebase_repository import CiFirebaseRepository
from tests.test_data.ci_test_data import (
    mock_ci_metadata,
    mock_classifier_type,
    mock_classifier_value,
    mock_language,
    mock_survey_id,
)

client = TestClient(app)
settings = Settings()


@patch("app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.get_ci_metadata_collection")
class TestHttpGetCiMetadataV1:
    """Tests for the `http_get_ci_metadata_v1` endpoint"""

    base_url = "/v1/ci_metadata"
    query_params = GetCiMetadataV1Params(
        classifier_type=mock_classifier_type,
        classifier_value=mock_classifier_value,
        language=mock_language,
        survey_id=mock_survey_id,
    )
    url = f"{base_url}?{urlencode(query_params.__dict__)}"

    classifier_error = (
        f"{base_url}?classifier_type=bad_classifier&classifier_value={mock_classifier_value}"
        f"&language={mock_language}&survey_id={mock_survey_id}"
    )

    def test_endpoint_returns_200_if_ci_metadata_found(self, mocked_get_ci_metadata_collection):
        """
        this may fail
        Endpoint should return `HTTP_200_OK` and ci metadata collection as part of the response
        if ci metadata is found. Assert that the correct methods are called with the correct arguments.
        """
        # Update mocked function to return a list of valid ci metadata
        mocked_get_ci_metadata_collection.return_value = [mock_ci_metadata]

        response = client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [mock_ci_metadata.model_dump()]
        CiFirebaseRepository.get_ci_metadata_collection.assert_called_once_with(
            mock_survey_id, mock_classifier_type, mock_classifier_value, mock_language
        )

    def test_endpoint_returns_400_if_query_parameters_are_not_present(self, mocked_get_ci_metadata_collection):
        """
        Endpoint should return `HTTP_400_BAD_REQUEST` as part of the response if `classifier_type`, `classifier_value`
        `language` and/or `survey_id` are not part of the query string parameters
        """
        # Make request to base url without any query params
        response = client.get(self.base_url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["message"] == "Invalid search parameters provided"

    def test_endpoint_returns_400_if_invalid_classifier_is_used(self, mocked_get_ci_metadata_collection):
        """
        Endpoint should return `HTTP_400_BAD_REQUEST` as part of the response if `classifier_type`, `classifier_value`
        `language` and/or `survey_id` are not part of the query string parameters
        """
        # Make request to base url without any query params
        response = client.get(self.classifier_error)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["message"] == "Validation has failed"

    def test_endpoint_returns_404_if_ci_metadata_not_found(self, mocked_get_ci_metadata_collection):
        """
        Endpoint should return `HTTP_404_NOT_FOUND` and a string indicating a bad request
        as part of the response if ci metadata is not found
        """
        # Update mocked function to return `None` showing ci metadata is not found
        mocked_get_ci_metadata_collection.return_value = None

        response = client.get(self.url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["message"] == "No results found"
