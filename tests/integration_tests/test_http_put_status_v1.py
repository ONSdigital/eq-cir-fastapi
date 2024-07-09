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
        classifier_type = setup_payload["classifier_type"]
        classifier_value = setup_payload["classifier_value"]
        language = setup_payload["language"]
        querystring = urlencode(
            {
                "classifier_type": classifier_type,
                "classifier_value": classifier_value,
                "language": language,
                "survey_id": survey_id,
            }
        )
        # sends request to http_query_ci endpoint for data
        query_ci_pre_response = make_iap_request("GET", f"{self.get_metadata_url}?{querystring}")
        return query_ci_pre_response.json()

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
            "message": "No results found",
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
