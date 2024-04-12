from unittest.mock import patch
from urllib.parse import urlencode

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app
from app.repositories.firebase.ci_firebase_repository import CiFirebaseRepository
from app.models.requests import (
    GetCiSchemaV1Params,
)
from app.models.responses import BadRequest
from tests.test_data.ci_test_data import (
    mock_survey_id, 
    mock_form_type, 
    mock_language,
    mock_ci_metadata,
)

client = TestClient(app)
settings = Settings()


@patch("app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.get_latest_ci_metadata")
@patch("app.repositories.buckets.ci_schema_bucket_repository.CiSchemaBucketRepository.retrieve_ci_schema")
class TestHttpGetCiSchemaV1:
    """Tests for the `http_get_ci_schema_v1` endpoint"""

    base_url = "/v1/retrieve_collection_instrument"
    query_params = GetCiSchemaV1Params(form_type=mock_form_type, language=mock_language, survey_id=mock_survey_id)
    url = f"{base_url}?{urlencode(query_params.__dict__)}"

    def test_endpoint_returns_200_if_ci_schema_found(self, mocked_retrieve_ci_schema, mocked_get_latest_ci_metadata):
        """
        Endpoint should return `HTTP_200_OK` and ci schema as part of the response if ci schema is found.
        Assert the mocked function is called with the correct params.
        """
        # mocked function to return valid ci metadata, indicating latest version of ci metadata is found
        mocked_get_latest_ci_metadata.return_value = mock_ci_metadata
        # mocked function to return valid ci, indicating ci schema is found from bucket
        mocked_retrieve_ci_schema.return_value = mock_ci_metadata.__dict__
        
        response = client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_ci_metadata.__dict__
        CiFirebaseRepository.get_latest_ci_metadata.assert_called_once_with(
            mock_survey_id, mock_form_type, mock_language
        )


    def test_endpoint_returns_BadRequest_if_metadata_not_found(self, mocked_retrieve_ci_schema, mocked_get_latest_ci_metadata):
        """
        Endpoint should return `HTTP_404_NOT_FOUND` and a string as part of the response if metadata is not
        found
        """
        # mocked function to return valid ci metadata, indicating latest version of ci metadata is not found
        mocked_get_latest_ci_metadata.return_value = None

        expected_response = BadRequest(message=f"No metadata found for: {self.query_params.__dict__}")
        response = client.get(self.url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == expected_response.__dict__


    def test_endpoint_returns_BadRequest_if_schema_not_found(self, mocked_retrieve_ci_schema, mocked_get_latest_ci_metadata):
        """
        Endpoint should return `HTTP_404_NOT_FOUND` and a string as part of the response if schema is not
        found
        """
        # mocked function to return valid ci metadata, indicating latest version of ci metadata is found
        mocked_get_latest_ci_metadata.return_value = mock_ci_metadata
        # mocked function to return `None`, indicating ci schema is not found from bucket
        mocked_retrieve_ci_schema.return_value = None

        expected_response = BadRequest(message=f"No schema found for: {self.query_params.__dict__}")
        response = client.get(self.url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == expected_response.__dict__


    def test_endpoint_returns_400_if_query_parameters_are_not_present(self, mocked_retrieve_ci_schema, mocked_get_latest_ci_metadata):
        """
        Endpoint should return `HTTP_400_BAD_REQUEST` as part of the response if `form_type`,
        `language` and/or `survey_id` are not part of the querystring parameters
        """
        # Make request to base url without any query params
        response = client.get(self.base_url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST