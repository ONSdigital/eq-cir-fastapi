from unittest.mock import patch
from urllib.parse import urlencode

from fastapi import status
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app
from app.models.requests import GetCiMetadataV3Params
from app.repositories.firebase.ci_firebase_repository import CiFirebaseRepository
from tests.test_data.ci_test_data import (
    mock_ci_metadata_list,
    mock_id, mock_ci_metadata_v2,
)

client = TestClient(app)
settings = Settings()


@patch("app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.get_ci_metadata_with_id")
class TestHttpGetCiMetadataV2:
    """Tests for the `http_get_ci_metadata_v2` endpoint"""

    base_url = "/v3/ci_metadata"

    query_params = GetCiMetadataV3Params(
        guid=mock_id,
    )
    url = f"{base_url}?{urlencode(query_params.__dict__)}"

    guid_error = (
        f"{base_url}?guid="
    )

    def test_endpoint_returns_200_if_ci_metadata_found_with_query(
        self,
        mocked_get_ci_metadata_with_id
    ):
        """
        Endpoint should return `HTTP_200_OK` and ci metadata collection as part of the response if ci metadata is found if
        queried with params.
        Assert the mocked function is called with the correct params.
        """
        # Update mocked function to return a list of valid ci metadata
        mocked_get_ci_metadata_with_id.return_value = mock_ci_metadata_v2.model_dump()

        response = client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()== mock_ci_metadata_v2.model_dump()

    def test_endpoint_returns_200_if_ci_metadata_found_with_query_without_status(
        self,
        mocked_get_ci_metadata_with_id
    ):
        """
        Endpoint should return `HTTP_200_OK` and ci metadata collection as part of the response if ci metadata is found if
        queried with params without status.
        Assert the mocked function is called with the correct params.
        """
        # Update mocked function to return a list of valid ci metadata
        mocked_get_ci_metadata_with_id.return_value = mock_ci_metadata_v2.model_dump()

        response = client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_ci_metadata_v2.model_dump()

    def test_endpoint_returns_200_if_ci_metadata_found_with_empty_query(
        self,
        mocked_get_ci_metadata_with_id,
    ):
        """
        Endpoint should return `HTTP_200_OK` and ci metadata collection as part of the response if ci metadata is found with
        empty query params. An empty request is still valid for this endpoint.
        Assert the mocked function is called.
        """
        # Update mocked function to return a list of valid ci metadata
        mocked_get_ci_metadata_with_id.return_value = mock_ci_metadata_v2.model_dump()
        # Make request to base url without any query params
        response = client.get(self.base_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_ci_metadata_v2.model_dump()


    def test_endpoint_returns_404_if_ci_metadata_not_found(
        self,
        mocked_get_ci_metadata_with_id,
    ):
        """
        Endpoint should return `HTTP_404_NOT_FOUND` and a string indicating a bad request
        as part of the response if ci metadata is not found
        """
        # Update mocked function to return `None` showing ci metadata is not found
        mocked_get_ci_metadata_with_id.return_value = None

        response = client.get(self.url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["message"] == "No results found"

    def test_endpoint_returns_400_if_guid_empty(
        self,
            mocked_get_ci_metadata_with_id,
    ):
        """
        Endpoint should return `HTTP_400_BAD_REQUEST`
        """
        # Make request to base url without any query params
        response = client.get(self.guid_error)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["message"] == "Invalid search parameters provided"
