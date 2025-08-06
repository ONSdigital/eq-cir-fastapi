import json
from urllib.parse import urlencode

import pytest
from fastapi import status

from app.config import settings
from app.events.subscriber import Subscriber
from tests.integration_tests.helpers.integration_helpers import pubsub_setup, pubsub_teardown
from tests.integration_tests.helpers.pubsub_helper import ci_pubsub_helper
from tests.integration_tests.utils import make_iap_request


class TestDeleteCiV1:
    """Tests for the `http_delete_ci_v1` endpoint"""

    base_url = "/v1/dev/teardown"
    post_url = "/v1/publish_collection_instrument"

    @classmethod
    def setup_class(cls) -> None:
        pubsub_teardown(ci_pubsub_helper, settings.SUBSCRIPTION_ID)

    def test_can_delete_ci_returns_200(self, setup_payload):
        """
        What am I testing:
           http_delete_ci should delete the metadata and schema and return the correct response.
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
            http_delete_ci should delete the metadata and schema and return the bad request if `survey_id` querystring
            parameter is malformed or missing.
        """
        querystring = urlencode({"my_bad": "param"})
        # Send request to http_delete_ci endpoint
        response = make_iap_request("DELETE", f"{self.base_url}?{querystring}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_can_delete_ci_returns_404_not_found(self):
        """
        What am I testing:
        http_delete_ci should delete the metadata and schema and return the 404 not found bad request.
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
        http_delete_ci should return a 401 unauthorized error if the endpoint is requested with an unauthorized token.
        """
        if settings.CONF == "local-int-tests":
            pytest.skip("Skipping test_delete_ci_returns_unauthorized_request on local environment")

        survey_id = setup_payload["survey_id"]
        querystring = urlencode({"survey_id": survey_id})
        response = make_iap_request("DELETE", f"{self.base_url}?{querystring}", unauthenticated=True)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
