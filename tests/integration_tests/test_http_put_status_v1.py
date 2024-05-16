from urllib.parse import urlencode

from fastapi import status

from app.events.subscriber import Subscriber
from tests.integration_tests.utils import make_iap_request


class TestPutStatusV1:
    """Tests for the `http_put_status_v1` endpoint."""

    base_url = "/v1/update_status"
    post_url = "/v1/publish_collection_instrument"
    get_metadata_url = "/v1/ci_metadata"
    subscriber = Subscriber()

    def teardown_method(self):
        """
        This function deletes the test CI with survey_id:3456 at the end of each integration test to ensure it
        is not reflected in the firestore and schemas.
        """
        # Need to pull and acknowledge messages in any test where post_ci_v1 is called so the subscription doesn't get clogged
        self.subscriber.pull_messages_and_acknowledge()
        querystring = urlencode({"survey_id": 3456})
        make_iap_request("DELETE", f"/v1/dev/teardown?{querystring}")

    def return_query_ci(self, setup_payload):
        """
        This function, written to avoid duplication, sends request to http_query_ci endpoint and returns
        the response in JSON
        """
        survey_id = setup_payload["survey_id"]
        form_type = setup_payload["form_type"]
        language = setup_payload["language"]
        querystring = urlencode({"form_type": form_type, "language": language, "survey_id": survey_id})
        # sends request to http_query_ci endpoint for data
        query_ci_pre_response = make_iap_request("GET", f"{self.get_metadata_url}?{querystring}")
        return query_ci_pre_response.json()

    def test_post_ci_v1_returns_draft_and_put_status_v1_returns_published(self, setup_payload):
        """
        What am I testing:
        http_put_status_v1 should return a HTTP_200_OK and have the payload's status to published
        """
        # Posts the ci using http_post_ci endpoint
        make_iap_request("POST", f"{self.post_url}", json=setup_payload)
        query_ci_pre_response_data = self.return_query_ci(setup_payload)
        ci_id = query_ci_pre_response_data[0]["guid"]
        assert query_ci_pre_response_data[0]["status"] == "DRAFT"

        querystring = urlencode({"guid": ci_id})
        # sends request to http_put_status for updating status
        ci_update = make_iap_request("PUT", f"{self.base_url}?{querystring}")
        assert ci_update.status_code == status.HTTP_200_OK

        # returning text as opposed to json as its a string
        ci_update_data = ci_update.json()
        assert ci_update_data == "put_status_v1: CI status has been changed to PUBLISHED"

        query_ci_post_response_data = self.return_query_ci(setup_payload)

        assert query_ci_post_response_data[0]["status"] == "PUBLISHED"

    def test_post_ci_v1_returns_draft_and_put_status_v1_returns_already_published(self, setup_payload):
        """
        What am I testing:
        http_put_status_v1 should return a HTTP_200_OK and throw a message status is already changed to published.
        """
        # Posts the ci using http_post_ci endpoint
        make_iap_request("POST", f"{self.post_url}", json=setup_payload)
        query_ci_pre_response_data = self.return_query_ci(setup_payload)
        ci_id = query_ci_pre_response_data[0]["guid"]
        querystring = urlencode({"guid": ci_id})
        # Updating status twice to return already published
        ci_update = make_iap_request("PUT", f"{self.base_url}?{querystring}")
        assert ci_update.status_code == status.HTTP_200_OK

        # returning text as opposed to json as its a string
        ci_update_data = ci_update.json()
        assert ci_update_data == "put_status_v1: CI status has already been changed to PUBLISHED"

    def test_guid_not_found(self):
        """
        What am I testing:
        http_put_status_v1 should return a HTTP_404_NOT_FOUND if the guid is not found.
        """
        ci_id = "404"
        querystring = urlencode({"guid": ci_id})
        # sends request to http_put_status
        ci_update = make_iap_request("PUT", f"{self.base_url}?{querystring}")
        assert ci_update.status_code == status.HTTP_404_NOT_FOUND

        ci_update_data = ci_update.json()
        assert ci_update_data == {
            "message": "No schema found",
            "status": "error",
        }

    def test_put_status_returns_unauthorized_request(self):
        """
        What am I testing:
        http_put_status_v1 should return a 401 unauthorized error if the endpoint is requested with an unauthorized token.
        """
        ci_id = "401"
        querystring = urlencode({"guid": ci_id})
        # sends request to http_put_status
        ci_update = make_iap_request("PUT", f"{self.base_url}?{querystring}", unauthenticated=True)
        assert ci_update.status_code == status.HTTP_401_UNAUTHORIZED
