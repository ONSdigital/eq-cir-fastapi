from unittest.mock import patch
from urllib.parse import urlencode

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.models.requests import (
    GetCiMetadataV1Params,
    GetCiSchemaV1Params,
    GetCiSchemaV2Params,
)
from app.models.responses import BadRequest

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
        # Update mocked `get_ci_metadata_v1` to return list of valid ci metadata
        mocked_get_ci_metadata_v1.return_value = [self.mock_ci_metadata]

        response = client.get(self.url)
        assert response.json() == [self.mock_ci_metadata]

    def test_endpoint_returns_400_if_query_parameters_are_not_present(self, mocked_get_ci_metadata_v1):
        """
        Endpoint should return `HTTP_400_BAD_REQUEST` as part of the response if `form_type`,
        `language` and/or `survey_id` are not part of the querystring parameters
        """
        # Make request to base url without any query params
        response = client.get(self.base_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

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
        expected_response = BadRequest(message=f"No CI metadata found for: {self.query_params.__dict__}")
        response = client.get(self.url)
        assert response.json() == expected_response.__dict__


@patch("app.main.get_ci_schema_v1")
class TestHttpGetCiSchemaV1:
    """Tests for the `http_get_ci_schema_v1` endpoint"""

    mock_form_type = "t"
    mock_language = "em"
    mock_survey_id = "12124141"
    mock_id = "123578"

    mock_ci_metadata = {
        "data_version": "1",
        "form_type": mock_form_type,
        "language": mock_language,
        "schema_version": "12",
        "survey_id": mock_survey_id,
        "title": "test",
    }

    base_url = "/v1/retrieve_collection_instrument"
    query_params = GetCiSchemaV1Params(form_type=mock_form_type, language=mock_language, survey_id=mock_survey_id)
    url = f"{base_url}?{urlencode(query_params.__dict__)}"

    def test_endpoint_returns_200_if_ci_schema_found(self, mocked_get_ci_schema_v1):
        """
        Endpoint should return `HTTP_200_OK` as part of the response if ci schema is found
        """
        # mocked `get_ci_schema_v1` to return valid ci metadata
        mocked_get_ci_schema_v1.return_value = ("123578", self.mock_ci_metadata)

        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_endpoint_resturns_if_ci_schema_found(self, mocked_get_ci_schema_v1):
        """
        Endpoint should return ci schema as part of the response if ci metadata is found
        """
        mocked_get_ci_schema_v1.return_value = ("123578", self.mock_ci_metadata)

        response = client.get(self.url)
        assert response.json() == self.mock_ci_metadata

    def test_endpoint_returns_BadRequest_if_guid_not_found(self, mocked_get_ci_schema_v1):
        """
        Endpoint should return `BadRequest` as part of the response if metadata is not
        found
        """
        # Update mocked `get_ci_schema_v1` to return `None` showing ci metadata is not found
        mocked_get_ci_schema_v1.return_value = None, None
        expected_response = BadRequest(message=f"No metadata found for: {self.query_params.__dict__}")
        response = client.get(self.url)
        assert response.json() == expected_response.__dict__

    def test_endpoint_returns_BadRequest_if_schema_not_found(self, mocked_get_ci_schema_v1):
        """
        Endpoint should return `BadRequest` as part of the response if schema is not
        found
        """
        # Update mocked `get_ci_schema_v1` to return `None` showing ci metadata is not found
        mocked_get_ci_schema_v1.return_value = ("123578", None)
        expected_response = BadRequest(message=f"No schema found for: {self.query_params.__dict__}")
        response = client.get(self.url)
        assert response.json() == expected_response.__dict__

    def test_endpoint_returns_400_if_query_parameters_are_not_present(self, mocked_get_ci_metadata_v1):
        """
        Endpoint should return `HTTP_400_BAD_REQUEST` as part of the response if `form_type`,
        `language` and/or `survey_id` are not part of the querystring parameters
        """
        # Make request to base url without any query params
        response = client.get(self.base_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@patch("app.main.get_ci_schema_v2")
class TestHttpGetCiSchemaV2:
    """Tests for the `http_get_ci_schema_v2` endpoint"""

    mock_form_type = "t"
    mock_language = "em"
    mock_survey_id = "12124141"
    mock_id = "123578"

    mock_ci = {
        "data_version": "1",
        "form_type": mock_form_type,
        "language": mock_language,
        "schema_version": "12",
        "survey_id": mock_survey_id,
        "title": "test",
    }

    base_url = "/v2/retrieve_collection_instrument"
    query_params = GetCiSchemaV2Params(id=mock_id)
    url = f"{base_url}?{urlencode(query_params.__dict__)}"

    def test_endpoint_returns_200_if_ci_schema_found(self, mocked_get_ci_schema_v2):
        """
        Endpoint should return `HTTP_200_OK` as part of the response if ci schema is found
        """
        # mocked `get_ci_schema_v2` to return valid ci metadata
        mocked_get_ci_schema_v2.return_value = (self.mock_ci, self.mock_ci)

        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_endpoint_resturns_if_ci_schema_found(self, mocked_get_ci_schema_v2):
        """
        Endpoint should return ci schema as part of the response if ci metadata is found
        """
        mocked_get_ci_schema_v2.return_value = (self.mock_ci, self.mock_ci)

        response = client.get(self.url)
        assert response.json() == self.mock_ci

    def test_endpoint_returns_BadRequest_if_metadata_not_found(self, mocked_get_ci_schema_v2):
        """
        Endpoint should return `BadRequest` as part of the response if metadata is not
        found
        """
        # Update mocked `get_ci_schema_v2` to return `None` showing ci metadata is not found
        mocked_get_ci_schema_v2.return_value = None, None
        expected_response = BadRequest(message=f"No CI metadata found for: {self.mock_id}")
        response = client.get(self.url)
        assert response.json() == expected_response.__dict__

    def test_endpoint_returns_BadRequest_if_schema_not_found(self, mocked_get_ci_schema_v1):
        """
        Endpoint should return `BadRequest` as part of the response if schema is not
        found
        """
        # Update mocked `get_ci_schema_v2` to return `None` showing ci metadata is not found
        mocked_get_ci_schema_v1.return_value = (self.mock_ci, None)
        expected_response = BadRequest(message=f"No schema found for: {self.mock_id}")
        response = client.get(self.url)
        assert response.json() == expected_response.__dict__

    def test_endpoint_returns_400_if_query_parameters_are_not_present(self, mocked_get_ci_metadata_v1):
        """
        Endpoint should return `HTTP_400_BAD_REQUEST` as part of the response if `id` is not
        part of the querystring parameters
        """
        # Make request to base url without any query params
        response = client.get(self.base_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
