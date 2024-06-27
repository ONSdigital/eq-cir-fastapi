# from unittest.mock import patch
# from urllib.parse import urlencode

# from fastapi import status
# from fastapi.testclient import TestClient

# from app.config import Settings
# from app.main import app
# from app.models.requests import PutStatusV1Params
# from app.repositories.firebase.ci_firebase_repository import CiFirebaseRepository
# from tests.test_data.ci_test_data import (
#     mock_ci_metadata,
#     mock_ci_published_metadata,
#     mock_id,
# )

# client = TestClient(app)
# settings = Settings()


# @patch("app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.get_ci_metadata_with_id")
# @patch("app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.update_ci_metadata_status_to_published_with_id")
# class TestHttpPutStatusV1:
#     "Tests for for the `http_put_status_v1` endpoint"

#     base_url = "/v1/update_status/"
#     query_params = PutStatusV1Params(guid=mock_id)
#     url = f"{base_url}?{urlencode(query_params.__dict__)}"


#     def test_endpoint_returns_404_if_ci_metadata_not_found(
#         self,
#         mocked_update_ci_metadata_status_to_published_with_id,
#         mocked_get_ci_metadata_with_id,
#     ):
#         """
#         Endpoint should return `HTTP_404_NOT_FOUND` and a not found string if metadata is not found.
#         Assert mocked functions are called with the correct arguments.
#         Assert `update_ci_metadata_status_to_published_with_id` is not called.
#         """
#         # mocked function to return `None`, indicating ci metadata is not found
#         mocked_get_ci_metadata_with_id.return_value = None

#         response = client.put(self.url)

#         assert response.status_code == status.HTTP_404_NOT_FOUND
#         assert response.json()["message"] == "No results found"
#         CiFirebaseRepository.get_ci_metadata_with_id.assert_called_once_with(mock_id)
#         CiFirebaseRepository.update_ci_metadata_status_to_published_with_id.assert_not_called()

