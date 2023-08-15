from unittest.mock import patch
from urllib.parse import urlencode

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.models.requests import (
    GetCiMetadataV1Params,
    GetCiMetadataV2Params,
    GetCiSchemaV1Params,
    GetCiSchemaV2Params,
    Status,
    UpdateStatusV2Params,
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


@patch("app.main.get_ci_metadata_v2")
class TestHttpGetCiMetadataV2:
    """Tests for the `http_get_ci_metadata_v2` endpoint"""

    mock_survey_id = "12124141"
    mock_language = "em"
    mock_form_type = "t"
    mock_title = "test"
    mock_schema_version = "12"
    mock_data_version = "1"
    mock_status = "DRAFT"

    mock_ci_list = [
        {
            "survey_id": mock_survey_id,
            "form_type": mock_form_type,
            "language": mock_language,
            "title": "test1",
            "ci_version": 1,
        },
        {
            "survey_id": mock_survey_id,
            "form_type": mock_form_type,
            "language": mock_language,
            "title": "test2",
            "ci_version": 2,
        },
    ]

    base_url = "/v2/ci_metadata"
    query_params = GetCiMetadataV2Params(
        form_type=mock_form_type, language=mock_language, status=mock_status, survey_id=mock_survey_id
    )
    url = f"{base_url}?{urlencode(query_params.__dict__)}"

    def test_endpoint_returns_200_if_ci_metadata_found_with_query(self, mocked_get_ci_metadata_v2):
        """
        Endpoint should return `HTTP_200_OK` as part of the response if ci metadata is found if
        queried with params
        """
        # Update mocked `get_ci_metadata_v2` to return valid ci metadata
        mocked_get_ci_metadata_v2.return_value = self.mock_ci_list

        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_endpoint_returns_ci_data_if_ci_metadata_found_with_query(self, mocked_get_ci_metadata_v2):
        """
        Endpoint should return ci metadata as part of the response if ci metadata is found if
        queried with params
        """
        # Update mocked `get_ci_metadata_v2` to return list of valid ci metadata
        mocked_get_ci_metadata_v2.return_value = self.mock_ci_list

        response = client.get(self.url)
        assert response.json() == self.mock_ci_list

    def test_endpoint_returns_200_if_ci_metadata_found_with_empty_query(self, mocked_get_ci_metadata_v2):
        """
        Endpoint should return `HTTP_200_OK` as part of the response if ci metadata is found with
        empty query params. An empty request is still valid for this endpoint.
        """
        # Update mocked `get_ci_metadata_v2` to return valid ci metadata
        mocked_get_ci_metadata_v2.return_value = self.mock_ci_list
        # Make request to base url without any query params
        response = client.get(self.base_url)
        assert response.status_code == status.HTTP_200_OK

    def test_endpoint_returns_ci_data_if_ci_metadata_found_empty_query(self, mocked_get_ci_metadata_v2):
        """
        Endpoint should return ci metadata as part of the response if ci metadata is found with
        empty query params. An empty request is still valid for this endpoint.
        """
        # Update mocked `get_ci_metadata_v2` to return list of valid ci metadata
        mocked_get_ci_metadata_v2.return_value = self.mock_ci_list
        # Make request to base url without any query params
        response = client.get(self.base_url)
        assert response.json() == self.mock_ci_list

    def test_endpoint_returns_404_if_ci_metadata_not_found(self, mocked_get_ci_metadata_v2):
        """
        Endpoint should return `HTTP_404_NOT_FOUND` as part of the response if ci metadata is not
        found
        """
        # Update mocked `get_ci_metadata_v2` to return `None` showing ci metadata is not found
        mocked_get_ci_metadata_v2.return_value = None

        response = client.get(self.url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_endpoint_returns_bad_response_if_ci_metadata_not_found(self, mocked_get_ci_metadata_v2):
        """
        Endpoint should return a string indicating a bad request as part of the response if ci
        metadata is not found
        """
        # Update mocked `get_ci_metadata_v2` to return `None` showing ci metadata is not found
        mocked_get_ci_metadata_v2.return_value = None
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


@patch("app.main.post_ci_metadata_v1")
class TestHttpPostCiV1:
    """
    Tests for the `http_post_ci_v1` endpoint
    Calls to `post_ci_metadata_v1` are mocked out for these tests
    """

    post_data = PostCiMetadataV1PostData(
        survey_id=mock_survey_id,
        language=mock_language,
        form_type=mock_form_type,
        title=mock_title,
        schema_version=mock_schema_version,
        data_version=mock_data_version,
        sds_schema=mock_sds_schema,
    )
    url = "/v1/publish_collection_instrument"

    def test_endpoint_returns_200_if_ci_created_successfully(self, mocked_post_ci_metadata_v1):
        """
        Endpoint should return `HTTP_200_OK` as part of the response if new ci is created
        successfully
        """
        # Update mocked `post_ci_metadata_v1` to return valid ci metadata
        mocked_post_ci_metadata_v1.return_value = mock_ci_metadata

        response = client.post(self.url, headers={"ContentType": "application/json"}, json=self.post_data.__dict__)
        assert response.status_code == status.HTTP_200_OK

    def test_endpoint_returns_serialized_ci_metadata_if_ci_created_successfully(self, mocked_post_ci_metadata_v1):
        """
        Endpoint should return serialized ci metadata as part of the response if new ci is created
        successfully
        """
        # Update mocked `post_ci_metadata_v1` to return valid ci metadata
        mocked_post_ci_metadata_v1.return_value = mock_ci_metadata

        response = client.post(self.url, headers={"ContentType": "application/json"}, json=self.post_data.__dict__)
        assert response.json() == mock_ci_metadata.__dict__

    def test_endpoint_returns_400_if_no_post_data(self, mocked_post_ci_metadata_v1):
        """
        Endpoint should return `HTTP_400_BAD_REQUEST` if empty or incomplete post data is posted
        as part of the request
        """
        # Make request to base url without any post data
        response = client.post(self.url, headers={"ContentType": "application/json"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_endpoint_returns_500_if_transaction_failed(self, mocked_post_ci_metadata_v1):
        """
        Endpoint should return `HTTP_500_BAD_REQUEST` if transaction failed
        """
        mocked_post_ci_metadata_v1.side_effect = Exception()
        response = client.post(self.url, headers={"ContentType": "application/json"}, json=self.post_data.__dict__)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@patch("app.main.put_status_v1")
class TestPutStatusV1:
    "Tests for Update Status Endpoint"

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

    base_url = "/v1/update_status/"
    query_params = UpdateStatusV2Params(id=mock_id)
    url = f"{base_url}?{urlencode(query_params.__dict__)}"

    def test_endpoint_returns_200_if_Status_Updated(self, mocked_update_status_v1):
        """
        Endpoint should return `HTTP_200_OK` if status is updated to published
        """
        # mocked `get_ci_schema_v2` to return valid ci metadata

        self.mock_ci["status"] = Status.PUBLISHED.value
        mocked_update_status_v1.return_value = (self.mock_ci, True)
        response = client.put(self.url)
        assert response.status_code == status.HTTP_200_OK
        expected_message = f"CI status has been changed to published for {self.query_params.id}"
        assert expected_message in response.content.decode("utf-8")

    def test_endpoint_returns_200_if_Status_already_Updated(self, mocked_update_status_v1):
        """
        Endpoint should return `HTTP_200_OK` if status is already updated to published
        """
        # mocked `get_ci_schema_v2` to return valid ci metadata

        self.mock_ci["status"] = Status.PUBLISHED.value
        mocked_update_status_v1.return_value = (self.mock_ci, False)
        response = client.put(self.url)
        assert response.status_code == status.HTTP_200_OK
        expected_message = f"CI status has already been changed to Published for {self.query_params.id}"
        assert expected_message in response.content.decode("utf-8")

    def test_endpoint_returns_BadRequest_if_ci_metadata_not_found(self, mocked_update_status_v1):
        """
        Endpoint should return BadRequest if metadata is not found
        """
        mocked_update_status_v1.return_value = (None, False)
        expected_response = BadRequest(message=f"No CI metadata found for: {self.mock_id}")
        response = client.put(self.url)
        assert response.json() == expected_response.__dict__

    def test_endpoint_returns_400_if_query_parameters_are_not_present(self, mocked_update_status_v1):
        """
        Endpoint should return `HTTP_400_BAD_REQUEST` as part of the response if `id` is not
        part of the querystring parameters
        """
        # Make request to base url without any query params
        response = client.put(self.base_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_endpoint_returns_Exception_if_query_parameters_invalid(self, mocked_update_status_v1):
        """
        Endpoint should thrown an HTTP_400_BAD_REQUEST if invalid status parameter is present in the metadata
        """
        mocked_update_status_v1.return_value = (self.mock_ci, None)
        response = client.put(self.base_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
