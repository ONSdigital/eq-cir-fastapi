from unittest.mock import patch
from urllib.parse import urlencode

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.models.requests import GetCiMetadataV1Params, DeleteCiV1Params
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


@patch("app.main.delete_ci_v1")
class TestHttpDeleteCiV1:

    mock_survey_id = "12124141"

    base_url = "/v1/dev/teardown"
    query_params = DeleteCiV1Params(survey_id=mock_survey_id)
    url = f"{base_url}?{urlencode(query_params.__dict__)}"

def test_delete_ci_v1_can_delete_ci_and_return_200(self, mocked_delete_ci_v1):
    """
    Why am I testing:
        To check that a single metadata and schema are deleted.
    What am I testing:
        200 success message and survey_id deleted
    """
    mocked_delete_ci_v1.return_value = self.mock_survey_id

    response = client.delete(self.url)
    assert response.status_code == status.HTTP_200_OK


def test_delete_ci_v1_can_delete_mulitple_ci_and_return_200(mocker):
    """
    Why am I testing:
        To check that multiple metadata and schema are deleted.
    What am I testing:
        200 success message and survey_id deleted
    """
    mock_db = mocker.Mock()
    mock_transaction = MagicMock()
    mock_query_ci_by_survey_id = mocker.patch(
        "src.handlers.collection_instrument.query_ci_by_survey_id",
        return_value=["1256", "2345", "1456"],
    )
    mock_delete_ci_metadata = mocker.patch(
        "src.handlers.collection_instrument.delete_ci_metadata",
        return_value=None,
    )
    mock_delete_ci_schema = mocker.patch(
        "src.handlers.collection_instrument.delete_ci_schema",
        return_value=None,
    )
    mocker.patch("src.handlers.collection_instrument.db", new=mock_db)

    mock_request = {
        "survey_id": "3456",
    }
    mock_request = MockRequestArgs(mock_request)
    # set the __enter__ method of the mock transaction to return the mock transaction itself
    mock_transaction.__enter__.return_value = mock_transaction

    # set the __exit__ method of the mock transaction to do nothing
    mock_transaction.__exit__.return_value = None

    # set the __call__ method of the mock_db object to return the mock transaction
    mock_db.transaction.return_value = mock_transaction
    response = delete_ci_v1(mock_request)
    mock_response = "3456 deleted"
    expected_resp = good_response_200(mock_response), 200

    assert expected_resp == response
    mock_query_ci_by_survey_id.assert_called_once_with("3456")
    mock_delete_ci_metadata.assert_called_once_with("3456")
    mock_delete_ci_schema.assert_called_once_with(["1256", "2345", "1456"])
    mock_db.transaction.assert_called_once_with()


def test_delete_ci_v1_returns_400_given_invalid_survey_id(mocker):
    """
    Why am I testing:
         To check that a 400 error is returned if an ivalid survey_id is passed
     What am I testing:
         400 and Bad request: Survey ID must be an integer"
    """
    mock_request = {
        "survey_id": "abcd",
    }
    mock_request = MockRequestArgs(mock_request)
    response = delete_ci_v1(mock_request)

    mock_response = "Bad request: Survey ID must be an integer"
    expected_resp = bad_request(mock_response), 400
    assert expected_resp == response


def test_delete_ci_v1_returns_500_for_any_exception_for_metadata(mocker):
    """
    Why am I testing:
        To ensure any un-expected exception is handled when called for metadata
    What am I testing:
        Ability for API to return 500 response
    """
    mock_delete_ci_metadata = mocker.patch(
        "src.handlers.collection_instrument.delete_ci_metadata",
        return_value=None,
    )

    mock_request = {
        "survey_id": "3456",
    }
    mock_request = MockRequestArgs(mock_request)

    mock_delete_ci_metadata.side_effect = (Exception("Test"),)

    response = delete_ci_v1(mock_request)
    expected_resp = (internal_error("Something went wrong"), 500)

    assert expected_resp == response
    mock_delete_ci_metadata.assert_called_once_with("3456")


def test_delete_ci_v1_returns_500_for_any_exception_for_schema(mocker):
    """
     Why am I testing:
        To ensure any un-expected exception when called for schema
    What am I testing:
        Ability for API to return 500 response
    """
    mocker.patch(
        "src.handlers.collection_instrument.query_ci_by_survey_id",
        return_value="1",
    )
    mock_delete_ci_schema = mocker.patch(
        "src.handlers.collection_instrument.delete_ci_schema",
        return_value=None,
    )
    mock_request = {
        "survey_id": "3456",
    }
    mock_request = MockRequestArgs(mock_request)

    mock_delete_ci_schema.side_effect = (Exception("Test"),)

    response = delete_ci_v1(mock_request)
    expected_resp = (internal_error("Something went wrong"), 500)

    assert expected_resp == response
    mock_delete_ci_schema.assert_called_once_with("1")