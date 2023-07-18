from unittest.mock import patch
from urllib.parse import urlencode

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.models.requests import GetCiMetadataV1Params
from app.models.responses import bad_request

client = TestClient(app)


@patch("app.main.get_ci_metadata_v1")
class TestHttpGetCiMetadataV1:
    """Tests for the `http_get_ci_metadata_v1` endpoint"""

    mock_form_type = "t"
    mock_language = "em"
    mock_survey_id = "12124141"

    mock_ci_metadata = {
        "data_version": "1",
        "form_type": mock_form_type,
        "language": mock_language,
        "schema_version": "12",
        "survey_id": mock_survey_id,
        "title": "test",
    }

    base_url = "/v1/ci_metadata"
    query_params = GetCiMetadataV1Params(form_type=mock_form_type, language=mock_language, survey_id=mock_survey_id)
    url = f"{base_url}?{urlencode(query_params.__dict__)}"

    def test_endpoint_returns_200_if_ci_metadata_found(self, mocked_get_ci_metadata_v1):
        """
        Endpoint should return `HTTP_200_OK` as part of the response if ci metadata is found
        """
        # Update mocked `get_ci_metadata_v1` to return valid ci metadata
        mocked_get_ci_metadata_v1.return_value = self.mock_ci_metadata

        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_endpoint_returns_ci_data_if_ci_metadata_found(self, mocked_get_ci_metadata_v1):
        """
        Endpoint should return ci metadata as part of the response if ci metadata is found
        """
        # Update mocked `get_ci_metadata_v1` to return valid ci metadata
        mocked_get_ci_metadata_v1.return_value = self.mock_ci_metadata

        response = client.get(self.url)
        assert response.json() == self.mock_ci_metadata

    def test_endpoint_returns_404_if_ci_metadata_not_found(self, mocked_get_ci_metadata_v1):
        """
        Endpoint should return `HTTP_404_NOT_FOUND` as part of the response if ci metadata is not
        found
        """
        # Update mocked `get_ci_metadata_v1` to return `None` showing ci metadata is not found
        mocked_get_ci_metadata_v1.return_value = None

        response = client.get(self.url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_endpoint_returns_bad_response_if_ci_metadata_not_found(self, mocked_get_ci_metadata_v1):
        """
        Endpoint should return a string indicating a bad request as part of the response if ci
        metadata is not found
        """
        # Update mocked `get_ci_metadata_v1` to return `None` showing ci metadata is not found
        mocked_get_ci_metadata_v1.return_value = None

        response = client.get(self.url)
        assert response.json() == bad_request(f"No CI metadata found for: {self.query_params.__dict__}")
