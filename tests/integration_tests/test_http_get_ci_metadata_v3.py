from urllib.parse import urlencode

import pytest
from fastapi import status

from app.config import settings
from app.services.ci_classifier_service import CiClassifierService
from tests.integration_tests.utils import make_iap_request


class TestGetCiMetadataV2:
    """Tests for the `http_get_ci_metadata_v2` endpoint."""

    base_url = "/v3/ci_metadata"
    post_url = "/v1/publish_collection_instrument"

    def teardown_method(self):
        """
        This function deletes the test CI with survey_id:3456 at the end of each integration test to ensure it
        is not reflected in the firestore and schemas.
        """
        querystring = urlencode({"survey_id": 3456})
        make_iap_request("DELETE", f"/v1/dev/teardown?{querystring}")

    def test_get_ci_metadata_v3_returns_200(self, setup_payload):
        """
        What am I testing:
        http_get_ci_metadata_v3 should return 1 metadata if the guid matches
        """

        post_response = make_iap_request("POST", f"{self.post_url}", json=setup_payload)

        guid = post_response.json()["guid"]

        get_ci_metadata_v2_payload = {
            "guid": guid
        }
        querystring = urlencode(get_ci_metadata_v2_payload)

        # sends request to http_get_ci_metadata_v3 endpoint for data
        get_ci_metadata_v3_response = make_iap_request("GET", f"{self.base_url}?{querystring}")

        assert get_ci_metadata_v3_response.status_code == status.HTTP_200_OK

        get_ci_metadata_v3_response_data = get_ci_metadata_v3_response.json()
        assert get_ci_metadata_v3_response_data == post_response.json()

    def test_metadata_query_v3_returns_404(self, setup_payload):
        """
        What am I testing:
        http_get_ci metadata_v3 should return 404 status code if the guid does not match any existing CI.
        """
        make_iap_request("POST", f"{self.post_url}", json=setup_payload)

        get_ci_metadata_v3_payload = {
            "guid": "123456" # guid that does not exist
        }
        querystring = urlencode(get_ci_metadata_v3_payload)

        # sends request to http_get_ci_metadata_v3 endpoint for data
        get_ci_metadata_v3_response = make_iap_request("GET", f"{self.base_url}?{querystring}")

        assert get_ci_metadata_v3_response.status_code == status.HTTP_404_NOT_FOUND
        query_ci_response = get_ci_metadata_v3_response.json()
        assert query_ci_response["message"] == "No results found"
        assert query_ci_response["status"] == "error"

    def test_metadata_query_ci_v2_returns_unauthorized_request(self, setup_payload):
        """
        What am I testing:
        http_get_ci metadata_v2 should return a 401 unauthorized error if the endpoint is requested with an unauthorized token.
        """
        if settings.CONF == "local-int-tests":
            pytest.skip("Skipping test_metadata_query_ci_v3_returns_unauthorized_request on local environment")

        get_ci_metadata_v3_payload = {
            "guid": "123456"
        }

        querystring = urlencode(get_ci_metadata_v3_payload)
        response = make_iap_request("GET", f"{self.base_url}?{querystring}", unauthenticated=True)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
