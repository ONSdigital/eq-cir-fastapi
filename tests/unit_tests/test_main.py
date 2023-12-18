import datetime
import uuid
from unittest.mock import patch
from urllib.parse import urlencode

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app
from app.models.requests import (
    DeleteCiV1Params,
    GetCiMetadataV1Params,
    GetCiMetadataV2Params,
    GetCiSchemaV1Params,
    GetCiSchemaV2Params,
    PostCiMetadataV1PostData,
    PutStatusV1Params,
)
from app.models.responses import BadRequest, CiMetadata, CiStatus

client = TestClient(app)
settings = Settings()


# Mock data for all tests
mock_data_version = "1"
mock_form_type = "t"
mock_id = str(uuid.uuid4())
mock_language = "em"
mock_schema_version = "12"
mock_sds_schema = ""
mock_status = "DRAFT"
mock_survey_id = "12124141"
mock_title = "test"
mock_description = "Version of CI is for March 2023 - APPROVED"

mock_ci_metadata = CiMetadata(
    ci_version=1,
    data_version=mock_data_version,
    form_type=mock_form_type,
    guid=mock_id,
    language=mock_language,
    published_at=datetime.datetime.utcnow().strftime(settings.PUBLISHED_AT_FORMAT),
    schema_version=mock_schema_version,
    sds_schema=mock_sds_schema,
    status=CiStatus.DRAFT.value,
    survey_id=mock_survey_id,
    title=mock_title,
    description=mock_description,
)


@patch("app.main.delete_ci_v1")
class TestHttpDeleteCiV1:
    """Tests for the `http_delete_ci_v1` endpoint"""

    base_url = "/v1/dev/teardown"
    query_params = DeleteCiV1Params(survey_id=mock_survey_id)
    url = f"{base_url}?{urlencode(query_params.__dict__)}"

    def test_endpoint_returns_200_if_ci_deleted(self, mocked_delete_ci_v1):
        """
        Endpoint should return `HTTP_200_OK` as part of the response if ci is found and deleted
        """
        # Update mocked `get_ci_metadata_v1` to return valid response
        mocked_delete_ci_v1.return_value = f"{self.query_params.survey_id} deleted"

        response = client.delete(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_endpoint_returns_correct_response_if_ci_deleted(self, mocked_delete_ci_v1):
        """
        Endpoint should return confirmation string as part of the response if ci is found and
        deleted
        """
        success_message = f"{self.query_params.survey_id} deleted"
        # Update mocked `get_ci_metadata_v1` to return valid response
        mocked_delete_ci_v1.return_value = success_message

        response = client.delete(self.url)
        assert response.json() == success_message

    def test_endpoint_returns_400_if_query_parameters_are_not_present(self, mocked_delete_ci_v1):
        """
        Endpoint should return `HTTP_400_BAD_REQUEST` as part of the response if `
        `survey_id` are not part of the querystring parameters
        """
        # Make request to base url without any query params
        response = client.delete(self.base_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_endpoint_returns_404_if_ci__not_found(self, mocked_delete_ci_v1):
        """
        Endpoint should return `HTTP_404_NOT_FOUND` as part of the response if no ci is found to
        delete
        """
        # Update mocked `get_ci_metadata_v1` to return `None` showing ci metadata is not found
        mocked_delete_ci_v1.return_value = None

        response = client.delete(self.url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_endpoint_returns_bad_response_if_ci_metadata_not_found(self, mocked_delete_ci_v1):
        """
        Endpoint should return a string indicating a bad request as part of the response if ci
        metadata is not found
        """
        # Update mocked `get_ci_metadata_v1` to return `None` showing ci metadata is not found
        mocked_delete_ci_v1.return_value = None
        expected_response = BadRequest(message=f"No CI found for: {self.query_params.__dict__}")
        response = client.delete(self.url)
        assert response.json() == expected_response.__dict__


@patch("app.main.get_ci_metadata_v1")
class TestHttpGetCiMetadataV1:
    """Tests for the `http_get_ci_metadata_v1` endpoint"""

    base_url = "/v1/ci_metadata"
    query_params = GetCiMetadataV1Params(form_type=mock_form_type, language=mock_language, survey_id=mock_survey_id)
    url = f"{base_url}?{urlencode(query_params.__dict__)}"

    def test_endpoint_returns_200_if_ci_metadata_found(self, mocked_get_ci_metadata_v1):
        """
        Endpoint should return `HTTP_200_OK` as part of the response if ci metadata is found
        """
        # Update mocked `get_ci_metadata_v1` to return valid ci metadata
        mocked_get_ci_metadata_v1.return_value = mock_ci_metadata.__dict__

        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_endpoint_returns_ci_data_if_ci_metadata_found(self, mocked_get_ci_metadata_v1):
        """
        Endpoint should return ci metadata as part of the response if ci metadata is found
        """
        # Update mocked `get_ci_metadata_v1` to return list of valid ci metadata
        mocked_get_ci_metadata_v1.return_value = [mock_ci_metadata.__dict__]

        response = client.get(self.url)
        assert response.json() == [mock_ci_metadata.__dict__]

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

    base_url = "/v1/retrieve_collection_instrument"
    query_params = GetCiSchemaV1Params(form_type=mock_form_type, language=mock_language, survey_id=mock_survey_id)
    url = f"{base_url}?{urlencode(query_params.__dict__)}"

    def test_endpoint_returns_200_if_ci_schema_found(self, mocked_get_ci_schema_v1):
        """
        Endpoint should return `HTTP_200_OK` as part of the response if ci schema is found
        """
        # mocked `get_ci_schema_v1` to return valid ci metadata
        mocked_get_ci_schema_v1.return_value = ("123578", mock_ci_metadata.__dict__)

        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_endpoint_resturns_if_ci_schema_found(self, mocked_get_ci_schema_v1):
        """
        Endpoint should return ci schema as part of the response if ci metadata is found
        """
        mocked_get_ci_schema_v1.return_value = ("123578", mock_ci_metadata.__dict__)

        response = client.get(self.url)
        assert response.json() == mock_ci_metadata.__dict__

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

    base_url = "/v2/retrieve_collection_instrument"
    query_params = GetCiSchemaV2Params(guid=mock_id)
    url = f"{base_url}?{urlencode(query_params.__dict__)}"

    def test_endpoint_returns_200_if_ci_schema_found(self, mocked_get_ci_schema_v2):
        """
        Endpoint should return `HTTP_200_OK` as part of the response if ci schema is found
        """
        # mocked `get_ci_schema_v2` to return valid ci metadata
        mocked_get_ci_schema_v2.return_value = (mock_ci_metadata.__dict__, mock_ci_metadata.__dict__)

        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_endpoint_resturns_if_ci_schema_found(self, mocked_get_ci_schema_v2):
        """
        Endpoint should return ci schema as part of the response if ci metadata is found
        """
        mocked_get_ci_schema_v2.return_value = (mock_ci_metadata.__dict__, mock_ci_metadata.__dict__)

        response = client.get(self.url)
        assert response.json() == mock_ci_metadata.__dict__

    def test_endpoint_returns_BadRequest_if_metadata_not_found(self, mocked_get_ci_schema_v2):
        """
        Endpoint should return `BadRequest` as part of the response if metadata is not
        found
        """
        # Update mocked `get_ci_schema_v2` to return `None` showing ci metadata is not found
        mocked_get_ci_schema_v2.return_value = None, None
        expected_response = BadRequest(message=f"No CI metadata found for: {self.query_params.guid}")
        response = client.get(self.url)
        assert response.json() == expected_response.__dict__

    def test_endpoint_returns_BadRequest_if_schema_not_found(self, mocked_get_ci_schema_v1):
        """
        Endpoint should return `BadRequest` as part of the response if schema is not
        found
        """
        # Update mocked `get_ci_schema_v2` to return `None` showing ci metadata is not found
        mocked_get_ci_schema_v1.return_value = (mock_ci_metadata.__dict__, None)
        expected_response = BadRequest(message=f"No schema found for: {self.query_params.guid}")
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
        description=mock_description,
    )
    url = "/v1/publish_collection_instrument"

    def test_endpoint_returns_200_if_ci_created_successfully(self, mocked_post_ci_metadata_v1):
        """
        Endpoint should return `HTTP_200_OK` as part of the response if new ci is created
        successfully
        """
        # Update mocked `post_ci_metadata_v1` to return valid ci metadata
        mocked_post_ci_metadata_v1.return_value = mock_ci_metadata

        response = client.post(self.url, headers={"ContentType": "application/json"}, json=self.post_data.model_dump())
        assert response.status_code == status.HTTP_200_OK

    def test_endpoint_returns_serialized_ci_metadata_if_ci_created_successfully(self, mocked_post_ci_metadata_v1):
        """
        Endpoint should return serialized ci metadata as part of the response if new ci is created
        successfully
        """
        # Update mocked `post_ci_metadata_v1` to return valid ci metadata
        mocked_post_ci_metadata_v1.return_value = mock_ci_metadata

        response = client.post(self.url, headers={"ContentType": "application/json"}, json=self.post_data.model_dump())
        assert response.json() == mock_ci_metadata.model_dump()

    def test_endpoint_returns_400_if_no_post_data(self, mocked_post_ci_metadata_v1):
        """
        Endpoint should return `HTTP_400_BAD_REQUEST` if empty or incomplete post data is posted
        as part of the request
        """
        # Make request to base url without any post data
        response = client.post(self.url, headers={"ContentType": "application/json"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("input_param", ["data_version", "form_type", "language", "survey_id", "title", "schema_version"])
    def test_endpoint_returns_400_if_required_field_none(self, mocked_post_ci_metadata_v1, input_param):
        """
        Endpoint should return `HTTP_400_BAD_REQUEST` if any required field in post data is `None`
        """
        # update `post_data` to contain `None` value for `input_param` field
        setattr(self.post_data, input_param, None)

        response = client.post(self.url, headers={"ContentType": "application/json"}, json=self.post_data.model_dump())
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("input_param", ["data_version", "form_type", "language", "survey_id", "title", "schema_version"])
    def test_endpoint_returns_400_if_required_field_empty_string(self, mocked_post_ci_metadata_v1, input_param):
        """
        Endpoint should return `HTTP_400_BAD_REQUEST` if any required field in post data is an
        empty string
        """
        # update `post_data` to contain empty string value for `input_param` field
        setattr(self.post_data, input_param, "")

        response = client.post(self.url, headers={"ContentType": "application/json"}, json=self.post_data.model_dump())
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("input_param", ["data_version", "form_type", "language", "survey_id", "title", "schema_version"])
    def test_endpoint_returns_400_if_required_field_whitespace(self, mocked_post_ci_metadata_v1, input_param):
        """
        Endpoint should return `HTTP_400_BAD_REQUEST` if any required field in post data is
        whitespace
        """
        # update `post_data` to contain whitespace value for `input_param` field
        setattr(self.post_data, input_param, " ")

        response = client.post(self.url, headers={"ContentType": "application/json"}, json=self.post_data.model_dump())
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_endpoint_returns_500_if_exception_occurs(self, mocked_post_ci_metadata_v1):
        """
        Endpoint should return `HTTP_500_INTERNAL_SERVER_ERROR` if an exception is raised by the
        `post_ci_metadata_v1` handler
        """
        # Update mocked `post_ci_metadata_v1` to raise a generic exception
        mocked_post_ci_metadata_v1.side_effect = Exception()

        with pytest.raises(Exception):
            response = client.post(self.url, headers={"ContentType": "application/json"}, json=self.post_data.model_dump())
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@patch("app.main.put_status_v1")
class TestPutStatusV1:
    "Tests for Update Status Endpoint"

    base_url = "/v1/update_status/"
    query_params = PutStatusV1Params(guid=mock_id)
    url = f"{base_url}?{urlencode(query_params.__dict__)}"

    def test_endpoint_returns_200_if_Status_Updated(self, mocked_update_status_v1):
        """
        Endpoint should return `HTTP_200_OK` if status is updated to published
        """
        # mocked `get_ci_schema_v2` to return valid ci metadata

        mocked_update_status_v1.return_value = (mock_ci_metadata.__dict__, True)
        response = client.put(self.url)
        assert response.status_code == status.HTTP_200_OK
        expected_message = f"CI status has been changed to Published for {self.query_params.guid}."
        assert expected_message in response.content.decode("utf-8")

    def test_endpoint_returns_200_if_Status_already_Updated(self, mocked_update_status_v1):
        """
        Endpoint should return `HTTP_200_OK` if status is already updated to published
        """
        # mocked `get_ci_schema_v2` to return valid ci metadata
        mocked_update_status_v1.return_value = (mock_ci_metadata.__dict__, False)
        response = client.put(self.url)
        assert response.status_code == status.HTTP_200_OK
        expected_message = f"CI status has already been changed to Published for {self.query_params.guid}"
        assert expected_message in response.content.decode("utf-8")

    def test_endpoint_returns_BadRequest_if_ci_metadata_not_found(self, mocked_update_status_v1):
        """
        Endpoint should return BadRequest if metadata is not found
        """
        mocked_update_status_v1.return_value = (None, False)
        expected_response = BadRequest(message=f"No CI metadata found for: {mock_id}")
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
        mocked_update_status_v1.return_value = (mock_ci_metadata.__dict__, "UNKOWN")
        response = client.put(self.base_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
