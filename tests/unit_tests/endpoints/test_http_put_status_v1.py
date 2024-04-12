from unittest.mock import patch
from urllib.parse import urlencode

from fastapi import status
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app
from app.models.requests import PutStatusV1Params
from app.models.responses import BadRequest
from app.repositories.firebase.ci_firebase_repository import CiFirebaseRepository
from tests.test_data.ci_test_data import (
    mock_ci_metadata,
    mock_ci_published_metadata,
    mock_id,
)

client = TestClient(app)
settings = Settings()


@patch(
    "app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.get_ci_metadata_with_id"
)
@patch(
    "app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.update_ci_metadata_status_to_published_with_id"
)
class TestHttpPutStatusV1:
    "Tests for for the `http_put_status_v1` endpoint"

    base_url = "/v1/update_status/"
    query_params = PutStatusV1Params(guid=mock_id)
    url = f"{base_url}?{urlencode(query_params.__dict__)}"

    def test_endpoint_returns_200_if_status_updated(
        self,
        mocked_update_ci_metadata_status_to_published_with_id,
        mocked_get_ci_metadata_with_id,
    ):
        """
        Endpoint should return `HTTP_200_OK` and a update successful string if status is updated to published.
        Assert mocked functions are called with the correct arguments.
        """
        # mocked function to return valid ci metadata, indicating ci metadata is found
        mocked_get_ci_metadata_with_id.return_value = mock_ci_metadata

        expected_message = (
            f"CI status has been changed to Published for {self.query_params.guid}."
        )
        response = client.put(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert expected_message in response.content.decode("utf-8")
        CiFirebaseRepository.get_ci_metadata_with_id.assert_called_once_with(mock_id)
        CiFirebaseRepository.update_ci_metadata_status_to_published_with_id.assert_called_once_with(
            mock_id
        )

    def test_endpoint_returns_200_if_status_already_updated(
        self,
        mocked_update_ci_metadata_status_to_published_with_id,
        mocked_get_ci_metadata_with_id,
    ):
        """
        Endpoint should return `HTTP_200_OK` and a CI already published string
        if status is already updated to published.
        Assert mocked functions are called with the correct arguments.
        Assert `update_ci_metadata_status_to_published_with_id` is not called.
        """
        # mocked function to return an already published ci metadata, indicating ci metadata is found but published
        mocked_get_ci_metadata_with_id.return_value = mock_ci_published_metadata

        expected_message = f"CI status has already been changed to Published for {self.query_params.guid}"
        response = client.put(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert expected_message in response.content.decode("utf-8")
        CiFirebaseRepository.get_ci_metadata_with_id.assert_called_once_with(mock_id)
        CiFirebaseRepository.update_ci_metadata_status_to_published_with_id.assert_not_called()

    def test_endpoint_returns_BadRequest_if_ci_metadata_not_found(
        self,
        mocked_update_ci_metadata_status_to_published_with_id,
        mocked_get_ci_metadata_with_id,
    ):
        """
        Endpoint should return `HTTP_404_NOT_FOUND` and a not found string if metadata is not found.
        Assert mocked functions are called with the correct arguments.
        Assert `update_ci_metadata_status_to_published_with_id` is not called.
        """
        # mocked function to return `None`, indicating ci metadata is not found
        mocked_get_ci_metadata_with_id.return_value = None

        expected_response = BadRequest(message=f"No CI metadata found for: {mock_id}")
        response = client.put(self.url)

        assert response.json() == expected_response.__dict__
        CiFirebaseRepository.get_ci_metadata_with_id.assert_called_once_with(mock_id)
        CiFirebaseRepository.update_ci_metadata_status_to_published_with_id.assert_not_called()

    def test_endpoint_returns_400_if_query_parameters_are_not_present(
        self,
        mocked_update_ci_metadata_status_to_published_with_id,
        mocked_get_ci_metadata_with_id,
    ):
        """
        Endpoint should return `HTTP_400_BAD_REQUEST` as part of the response if `id` is not
        part of the querystring parameters
        """
        # Make request to base url without any query params
        response = client.put(self.base_url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_endpoint_returns_Exception_if_query_parameters_invalid(
        self,
        mocked_update_ci_metadata_status_to_published_with_id,
        mocked_get_ci_metadata_with_id,
    ):
        """
        Endpoint should return an `HTTP_400_BAD_REQUEST` as part of the response if invalid
        query parameter is present in the request
        """
        # Make request to base url without any query params
        response = client.put(self.base_url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
