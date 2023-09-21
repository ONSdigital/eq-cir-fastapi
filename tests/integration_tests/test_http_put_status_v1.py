from urllib.parse import urlencode

from fastapi import status

from app.events.subscriber import Subscriber
from tests.integration_tests.utils import make_iap_request


class TestPutStatusV1:
    base_url = "/v1/update_status"
    subscriber = Subscriber()

    def teardown_method(self):
        print(": tearing down")
        querystring = urlencode({"survey_id": 3456})
        make_iap_request("DELETE", f"/v1/dev/teardown?{querystring}")

    def return_query_ci(self, setup_payload):
        survey_id = setup_payload["survey_id"]
        form_type = setup_payload["form_type"]
        language = setup_payload["language"]
        querystring = urlencode({"form_type": form_type, "language": language, "survey_id": survey_id})
        # sends request to http_query_ci endpoint for data
        query_ci_pre_response = make_iap_request("GET", f"/v1/ci_metadata?{querystring}")
        return query_ci_pre_response.json()

    def test_post_ci_v1_returns_draft_and_put_status_v1_returns_published(self, setup_payload):
        make_iap_request("POST", "/v1/publish_collection_instrument", json=setup_payload)
        self.subscriber.pull_messages_and_acknowledge()
        query_ci_pre_response_data = self.return_query_ci(setup_payload)
        ci_id = query_ci_pre_response_data[0]["id"]
        assert query_ci_pre_response_data[0]["status"] == "DRAFT"

        querystring = urlencode({"guid": ci_id})
        ci_update = make_iap_request("PUT", f"{self.base_url}?{querystring}")
        assert ci_update.status_code == status.HTTP_200_OK

        # returning text as opposed to json as its a string
        ci_update_data = ci_update.json()
        assert ci_update_data == f"CI status has been changed to Published for {ci_id}."

        query_ci_post_response_data = self.return_query_ci(setup_payload)

        assert query_ci_post_response_data[0]["id"] == ci_id
        assert query_ci_post_response_data[0]["status"] == "PUBLISHED"

    def test_post_ci_v1_returns_draft_and_put_status_v1_returns_already_published(self, setup_payload):
        make_iap_request("POST", "/v1/publish_collection_instrument", json=setup_payload)
        self.subscriber.pull_messages_and_acknowledge()
        query_ci_pre_response_data = self.return_query_ci(setup_payload)
        print(query_ci_pre_response_data)
        ci_id = query_ci_pre_response_data[0]["id"]
        querystring = urlencode({"guid": ci_id})
        # Updating status twice to return already published
        ci_update = make_iap_request("PUT", f"{self.base_url}?{querystring}")
        ci_update = make_iap_request("PUT", f"{self.base_url}?{querystring}")
        assert ci_update.status_code == status.HTTP_200_OK

        # returning text as opposed to json as its a string
        ci_update_data = ci_update.json()
        assert ci_update_data == f"CI status has already been changed to Published for {ci_id}."

        query_ci_post_response_data = self.return_query_ci(setup_payload)

        assert query_ci_post_response_data[0]["id"] == ci_id
        assert query_ci_post_response_data[0]["status"] == "PUBLISHED"

    def test_guid_not_found(self):
        ci_id = "404"
        querystring = urlencode({"guid": ci_id})
        ci_update = make_iap_request("PUT", f"{self.base_url}?{querystring}")
        assert ci_update.status_code == status.HTTP_404_NOT_FOUND

        ci_update_data = ci_update.json()
        assert ci_update_data == {
            "message": f"No CI metadata found for: {ci_id}",
            "status": "error",
        }
