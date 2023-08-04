import json
from urllib.parse import urlencode

from fastapi import status

from app.events.subscriber import Subscriber
from tests.integration_tests.utils import delete_docs, make_iap_request, post_ci_v1


class TestDeleteCiV1:
    subscriber = Subscriber()

    def test_can_delete_ci_returns_200(self, setup_payload):
        """
        What am I testing:
            Delete the metadata and schema and return the correct response.
        """
        # Create a CI to delete later and confirm it worked
        response = post_ci_v1(setup_payload)
        assert response.status_code == status.HTTP_200_OK

        self.subscriber.pull_messages_and_acknowledge()
        response = delete_docs("3456")
        assert response.text == json.dumps("3456 deleted")
        assert response.status_code == status.HTTP_200_OK

    def test_can_delete_ci_returns_400(self):
        """
        What am I testing:
            Delete the metadata and schema and return the bad request if `survey_id` querystring
            parameter is malformed or missing.
        """
        querystring = urlencode({"my_bad": "param"})

        response = make_iap_request("DELETE", f"/v1/dev/teardown?{querystring}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_can_delete_ci_returns_404_not_found(self):
        """
        What am I testing:
            Delete the metadata and schema and return the 404 not found bad request.
        """
        survey_id = "abcd"

        response = delete_docs(survey_id)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response = response.json()
        assert response["message"] == f"No CI found for: {{'survey_id': '{survey_id}'}}"
        assert response["status"] == "error"
