import json
from urllib.parse import urlencode

from fastapi import status

from app.events.subscriber import Subscriber
from tests.integration_tests.utils import make_iap_request


class TestDeleteCiV1:
    """Tests for the `http_delete_ci_v1` endpoint"""

    base_url = "/v1/dev/teardown"
    subscriber = Subscriber()

    def test_can_delete_ci_returns_200(self, setup_payload):
        """
        What am I testing:
            Delete the metadata and schema and return the correct response.
        """
        survey_id = setup_payload["survey_id"]
        querystring = urlencode({"survey_id": survey_id})

        # Create a CI to delete later and confirm it worked
        response = make_iap_request("POST", "/v1/publish_collection_instrument", json=setup_payload)
        assert response.status_code == status.HTTP_200_OK

        self.subscriber.pull_messages_and_acknowledge()
        response = make_iap_request("DELETE", f"{self.base_url}?{querystring}")
        assert response.text == f"{survey_id} deleted"
        assert response.status_code == status.HTTP_200_OK

    def test_can_delete_ci_returns_400(self):
        """
        What am I testing:
            Delete the metadata and schema and return the bad request if `survey_id` querystring
            parameter is malformed or missing.
        """
        querystring = urlencode({"my_bad": "param"})

        response = make_iap_request("DELETE", f"{self.base_url}?{querystring}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_can_delete_ci_returns_404_not_found(self):
        """
        What am I testing:
            Delete the metadata and schema and return the 404 not found bad request.
        """
        survey_id = "abcd"
        querystring = urlencode({"survey_id": survey_id})

        response = make_iap_request("DELETE", f"{self.base_url}?{querystring}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response = response.json()
        assert response["message"] == f"No CI found for: {{'survey_id': '{survey_id}'}}"
        assert response["status"] == "error"
