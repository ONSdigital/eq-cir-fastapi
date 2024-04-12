from unittest.mock import patch
from urllib.parse import urlencode

from fastapi import status
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app
from app.repositories.firebase.ci_firebase_repository import CiFirebaseRepository
from app.models.requests import (
    GetCiMetadataV2Params,
)
from app.models.responses import BadRequest
from tests.test_data.ci_test_data import (
    mock_survey_id,
    mock_form_type,
    mock_language,
    mock_status,
    mock_ci_metadata_list,
)

client = TestClient(app)
settings = Settings()


@patch("app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.get_ci_metadata_collection_with_status")
@patch("app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.get_ci_metadata_collection_without_status")
@patch("app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.get_ci_metadata_collection_only_with_status")
@patch("app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.get_all_ci_metadata_collection")
class TestHttpGetCiMetadataV2:
    """Tests for the `http_get_ci_metadata_v2` endpoint"""

    base_url = "/v2/ci_metadata"

    query_params = GetCiMetadataV2Params(
        form_type=mock_form_type, language=mock_language, status=mock_status, survey_id=mock_survey_id
    )
    url = f"{base_url}?{urlencode(query_params.__dict__)}"

    status_only_url = f"{base_url}?status={mock_status}"

    without_status_url = f"{base_url}?form_type={mock_form_type}&language={mock_language}&survey_id={mock_survey_id}"

    wrong_status_query_params = GetCiMetadataV2Params(
        form_type=mock_form_type, language=mock_language, status="WRONG_STATUS", survey_id=mock_survey_id
    )
    wrong_status_url = f"{base_url}?{urlencode(wrong_status_query_params.__dict__)}"

    def test_endpoint_returns_200_if_ci_metadata_found_with_query(
        self,
        mocked_get_all_ci_metadata_collection,
        mocked_get_ci_metadata_collection_only_with_status,
        mocked_get_ci_metadata_collection_without_status,
        mocked_get_ci_metadata_collection_with_status,
    ):
        """
        Endpoint should return `HTTP_200_OK` and ci metadata collection as part of the response if ci metadata is found if
        queried with params. Assert description is in response ci metadata.
        Assert the mocked function is called with the correct params.
        """
        # Update mocked function to return a list of valid ci metadata
        mocked_get_ci_metadata_collection_with_status.return_value = mock_ci_metadata_list

        response = client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == mock_ci_metadata_list.__len__()
        for i in range(len(response.json())):
            assert response.json()[i] == mock_ci_metadata_list[i].__dict__
            assert "description" in response.json()[i]

        CiFirebaseRepository.get_ci_metadata_collection_with_status.assert_called_once_with(
            mock_survey_id, mock_form_type, mock_language, mock_status
        )

    def test_endpoint_returns_200_if_ci_metadata_found_with_query_without_status(
        self,
        mocked_get_all_ci_metadata_collection,
        mocked_get_ci_metadata_collection_only_with_status,
        mocked_get_ci_metadata_collection_without_status,
        mocked_get_ci_metadata_collection_with_status,
    ):
        """
        Endpoint should return `HTTP_200_OK` and ci metadata collection as part of the response if ci metadata is found if
        queried with params without status. Assert description is in response ci metadata.
        Assert the mocked function is called with the correct params.
        """
        # Update mocked function to return a list of valid ci metadata
        mocked_get_ci_metadata_collection_without_status.return_value = mock_ci_metadata_list

        response = client.get(self.without_status_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == mock_ci_metadata_list.__len__()
        for i in range(len(response.json())):
            assert response.json()[i] == mock_ci_metadata_list[i].__dict__
            assert "description" in response.json()[i]

        CiFirebaseRepository.get_ci_metadata_collection_without_status.assert_called_once_with(
            mock_survey_id, mock_form_type, mock_language
        )

    def test_endpoint_returns_200_if_ci_metadata_found_with_empty_query(
        self,
        mocked_get_all_ci_metadata_collection,
        mocked_get_ci_metadata_collection_only_with_status,
        mocked_get_ci_metadata_collection_without_status,
        mocked_get_ci_metadata_collection_with_status,
    ):
        """
        Endpoint should return `HTTP_200_OK` and ci metadata collection as part of the response if ci metadata is found with
        empty query params. An empty request is still valid for this endpoint. Assert description is in response ci metadata.
        Assert the mocked function is called.
        """
        # Update mocked function to return a list of valid ci metadata
        mocked_get_all_ci_metadata_collection.return_value = mock_ci_metadata_list
        # Make request to base url without any query params
        response = client.get(self.base_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == mock_ci_metadata_list.__len__()
        for i in range(len(response.json())):
            assert response.json()[i] == mock_ci_metadata_list[i].__dict__
            assert "description" in response.json()[i]

        CiFirebaseRepository.get_all_ci_metadata_collection.assert_called_once()

    def test_endpoint_returns_200_if_ci_metadata_found_with_status_only_query(
        self,
        mocked_get_all_ci_metadata_collection,
        mocked_get_ci_metadata_collection_only_with_status,
        mocked_get_ci_metadata_collection_without_status,
        mocked_get_ci_metadata_collection_with_status,
    ):
        """
        Endpoint should return `HTTP_200_OK` and ci metadata collection as part of the response if ci metadata is found with
        status only query params. Assert description is in response ci metadata.
        Assert the mocked function is called with the correct params.
        """
        # Update mocked function to return a list of valid ci metadata
        mocked_get_ci_metadata_collection_only_with_status.return_value = mock_ci_metadata_list
        # Make request to base url only with status
        response = client.get(self.status_only_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == mock_ci_metadata_list.__len__()
        for i in range(len(response.json())):
            assert response.json()[i] == mock_ci_metadata_list[i].__dict__
            assert "description" in response.json()[i]

        CiFirebaseRepository.get_ci_metadata_collection_only_with_status.assert_called_once_with(mock_status)

    def test_endpoint_returns_404_if_ci_metadata_not_found(
        self,
        mocked_get_all_ci_metadata_collection,
        mocked_get_ci_metadata_collection_only_with_status,
        mocked_get_ci_metadata_collection_without_status,
        mocked_get_ci_metadata_collection_with_status,
    ):
        """
        Endpoint should return `HTTP_404_NOT_FOUND` and a string indicating a bad request
        as part of the response if ci metadata is not found
        """
        # Update mocked function to return `None` showing ci metadata is not found
        mocked_get_ci_metadata_collection_with_status.return_value = None

        expected_response = BadRequest(message=f"No CI metadata found for: {self.query_params.__dict__}")
        response = client.get(self.url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == expected_response.__dict__

    def test_endpoint_returns_400_if_status_is_invalid_in_query(
        self,
        mocked_get_all_ci_metadata_collection,
        mocked_get_ci_metadata_collection_only_with_status,
        mocked_get_ci_metadata_collection_without_status,
        mocked_get_ci_metadata_collection_with_status,
    ):
        """
        Endpoint should return `HTTP_400_BAD_REQUEST` and a string indicating a bad request
        as part of the response if status is invalid in query
        """
        response = client.get(self.wrong_status_url)
        expected_response = BadRequest(message=f"Status is invalid in query: {self.wrong_status_query_params.__dict__}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == expected_response.__dict__
