from unittest.mock import patch
from urllib.parse import urlencode

from fastapi.testclient import TestClient
from fastapi import status

from app.config import Settings
from app.main import app
from app.models.requests import PatchValidatorVersionV1Params
from tests.test_data.ci_test_data import (
    mock_validator_version_v2, mock_id, mock_ci_metadata_v2,
)

client = TestClient(app)
settings = Settings()


@patch("app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.get_ci_metadata_with_id")
@patch("app.repositories.buckets.ci_schema_bucket_repository.CiSchemaBucketRepository.retrieve_ci_schema")
@patch("app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.update_ci_metadata")
class TestHttpPatchValidatorVersionV1:
    """Tests for the `http_patch_ci_validator_version_v1` endpoint"""

    base_url = "/v1/update_validator_version"

    query_params = PatchValidatorVersionV1Params(
        guid=mock_id,
        validator_version=mock_validator_version_v2

    )
    url = f"{base_url}?{urlencode(query_params.__dict__)}"

    missing_validator_version = f"{base_url}?guid={query_params.guid}"

    missing_guid = f"{base_url}?validator_version={query_params.validator_version}"

    def test_endpoint_returns_200(self,
                                  mocked_update_ci_metadata,
                                  mocked_retrieve_ci_schema,
                                  mocked_get_ci_metadata_with_id):
        # mocked function to return valid ci metadata, indicating ci metadata is found
        mocked_get_ci_metadata_with_id.return_value = mock_ci_metadata_v2
        # mocked function to return valid ci schema, indicating ci schema is found from bucket
        mocked_retrieve_ci_schema.return_value = mock_ci_metadata_v2.__dict__

        response = client.patch(self.url)
        assert response.status_code == status.HTTP_200_OK
        print("mockdata")
        print(mock_ci_metadata_v2.model_dump())
        print("response")
        print(response.json())
        assert response.json() == mock_ci_metadata_v2.model_dump()

    def test_endpoint_metadata_not_found(self,
                                         mocked_get_ci_metadata_with_id,
                                         mocked_retrieve_ci_schema,
                                         mocked_update_ci_metadata):

        mocked_get_ci_metadata_with_id.return_value = None
        mocked_retrieve_ci_schema.return_value = None
        mocked_update_ci_metadata.return_value = None

        # Make request to base url without any query params
        response = client.patch(self.url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["message"] == "No results found"

    def test_endpoint_returns_400_no_validator_version(self,
                                                       mocked_get_ci_metadata_with_id,
                                                       mocked_retrieve_ci_schema,
                                                       mocked_update_ci_metadata):

        response = client.patch(self.missing_validator_version)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["message"] == "Invalid search parameters provided"

    def test_endpoint_returns_400_no_guid(self,
                                          mocked_get_ci_metadata_with_id,
                                          mocked_retrieve_ci_schema,
                                          mocked_update_ci_metadata):
        response = client.patch(self.missing_guid)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["message"] == "Invalid search parameters provided"
