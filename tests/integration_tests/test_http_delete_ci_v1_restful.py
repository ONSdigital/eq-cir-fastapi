import json
from urllib.parse import urlencode

import pytest
from fastapi import status

from app.config import settings
from tests.integration_tests.utils import make_iap_request, create_post_params


class TestDeleteCiV1Restful:
    """Tests for the `delete_collection_instrument` endpoint"""

    base_url = "/v1/collection-instruments"

    post_params = create_post_params(1)

    post_url = f"/v3/collection-instruments?{post_params[0]}"

    def test_can_delete_ci_returns_200(self, setup_payload):
        """
        What am I testing:
        delete_collection_instrument should delete the metadata and schema and return the correct response.
        """
        survey_id = setup_payload["survey_id"]
        querystring = urlencode({"survey_id": survey_id})

        # Create a CI to delete later and confirm it worked
        response = make_iap_request("POST", f"{self.post_url}", json=setup_payload)
        assert response.status_code == status.HTTP_200_OK

        # Send request to http_delete_ci endpoint
        response = make_iap_request("DELETE", f"{self.base_url}?{querystring}")
        assert response.text == json.dumps(f"CI metadata and schema successfully deleted for {survey_id}.")
        assert response.status_code == status.HTTP_200_OK

    def test_can_delete_ci_returns_400(self):
        """
        What am I testing:
        delete_collection_instrument should delete the metadata and schema and return the bad request if `survey_id` querystring
        parameter is malformed or missing.
        """
        querystring = urlencode({"my_bad": "param"})
        # Send request to http_delete_ci endpoint
        response = make_iap_request("DELETE", f"{self.base_url}?{querystring}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_can_delete_ci_returns_404_not_found(self):
        """
        What am I testing:
        delete_collection_instrument should delete the metadata and schema and return the 404 not found bad request.
        """
        survey_id = "abcd"
        querystring = urlencode({"survey_id": survey_id})
        # Send request to http_delete_ci endpoint
        response = make_iap_request("DELETE", f"{self.base_url}?{querystring}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["message"] == "No CI to delete"
        assert response.json()["status"] == "error"

    def test_delete_ci_returns_unauthorized_request(self, setup_payload):
        """
        What am I testing:
        delete_collection_instrument should return a 401 unauthorized error if the endpoint is requested with an unauthorized token.
        """
        if settings.CONF == "local-int-tests":
            pytest.skip("Skipping test_delete_ci_returns_unauthorized_request on local environment")

        survey_id = setup_payload["survey_id"]
        querystring = urlencode({"survey_id": survey_id})
        response = make_iap_request("DELETE", f"{self.base_url}?{querystring}", unauthenticated=True)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
