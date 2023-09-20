from urllib.parse import urlencode

from fastapi import status

from app.events.subscriber import Subscriber
from tests.integration_tests.utils import make_iap_request, post_ci_v1


class TestGetCiMetadataV2:
    base_url = "/v2/ci_metadata"
    subscriber = Subscriber()

    def teardown_method(self):
        print(": tearing down")
        querystring = urlencode({"survey_id": 3456})
        make_iap_request("DELETE", f"/v1/dev/teardown?{querystring}")

    def test_post_3_ci_with_same_metadata_get_ci_metadata_v2_returns_3(self, setup_payload):
        for _ in range(3):
            post_ci_v1(setup_payload)
            self.subscriber.pull_messages_and_acknowledge()

        get_ci_metadata_v2_payload = {
            "form_type": setup_payload["form_type"],
            "language": setup_payload["language"],
            "survey_id": setup_payload["survey_id"],
        }
        querystring = urlencode(get_ci_metadata_v2_payload)

        # sends request to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        get_ci_metadata_v2_response_data = get_ci_metadata_v2_response.json()

        assert len(get_ci_metadata_v2_response_data) == 3
        assert get_ci_metadata_v2_response_data[2]["ci_version"] == 1
        assert get_ci_metadata_v2_response_data[1]["ci_version"] == 2
        assert get_ci_metadata_v2_response_data[0]["ci_version"] == 3

    def test_post_ci_v1_returns_draft_and_put_status_v1_returns_published(self, setup_payload):
        for _ in range(3):
            post_ci_v1(setup_payload)
            self.subscriber.pull_messages_and_acknowledge()

        get_ci_metadata_v2_payload = {
            "form_type": setup_payload["form_type"],
            "language": setup_payload["language"],
            "status": setup_payload["status"],
            "survey_id": setup_payload["survey_id"],
        }

        querystring = urlencode(get_ci_metadata_v2_payload)

        # sends request to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        get_ci_metadata_v2_response_data = get_ci_metadata_v2_response.json()
        ci_id = get_ci_metadata_v2_response_data[0]["id"]
        assert get_ci_metadata_v2_response_data[0]["status"] == "DRAFT"
        querystring = urlencode({"guid": ci_id})
        ci_update = make_iap_request("PUT", f"/v1/update_status?{querystring}")
        assert ci_update.status_code == status.HTTP_200_OK
        # sends request to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_payload = {
            "form_type": setup_payload["form_type"],
            "language": setup_payload["language"],
            "status": "PUBLISHED",
            "survey_id": setup_payload["survey_id"],
        }
        querystring = urlencode(get_ci_metadata_v2_payload)

        # sends request to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        get_ci_metadata_v2_post_response_data = get_ci_metadata_v2_response.json()
        assert get_ci_metadata_v2_post_response_data[0]["status"] == "PUBLISHED"

    def test_get_ci_metadata_v2_returns_draft_and_put_ci_v1_returns_published(self, setup_payload):
        for _ in range(3):
            post_ci_v1(setup_payload)
            self.subscriber.pull_messages_and_acknowledge()
        get_ci_metadata_v2_payload = {"status": setup_payload["status"]}
        querystring = urlencode(get_ci_metadata_v2_payload)

        # sends request to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        get_ci_metadata_v2_response_data = get_ci_metadata_v2_response.json()
        assert get_ci_metadata_v2_response_data[0]["status"] == "DRAFT"
        # Making sure only the test data status is changed to published
        # sends request to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_payload = {
            "form_type": setup_payload["form_type"],
            "language": setup_payload["language"],
            "status": setup_payload["status"],
            "survey_id": setup_payload["survey_id"],
        }
        querystring = urlencode(get_ci_metadata_v2_payload)

        # sends request to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        get_ci_metadata_v2_response_data = get_ci_metadata_v2_response.json()
        ci_id = get_ci_metadata_v2_response_data[0]["id"]
        querystring = urlencode({"guid": ci_id})
        ci_update = make_iap_request("PUT", f"/v1/update_status?{querystring}")
        assert ci_update.status_code == status.HTTP_200_OK
        get_ci_metadata_v2_payload = {"status": setup_payload["status"]}
        querystring = urlencode(get_ci_metadata_v2_payload)

        # sends request to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_post_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        get_ci_metadata_v2_response_data = get_ci_metadata_v2_post_response.json()
        assert get_ci_metadata_v2_response_data[0]["status"] == "PUBLISHED"

    def test_get_ci_metadata_v2_returns_all_metadata(self):
        # Passing an empty list to the get_ci_metadata_v2
        get_ci_metadata_v2_response = make_iap_request("GET", f"{self.base_url}")
        get_ci_metadata_v2_response_data = get_ci_metadata_v2_response.json()
        assert len(get_ci_metadata_v2_response_data) > 0

    def test_post_ci_with_same_metadata_query_ci_returns_with_sds_schema(self, setup_payload):
        # post 3 ci with the same data
        setup_payload["sds_schema"] = "xx-ytr-1234-856"
        post_ci_v1(setup_payload)
        self.subscriber.pull_messages_and_acknowledge()
        get_ci_metadata_v2_payload = {
            "form_type": setup_payload["form_type"],
            "language": setup_payload["language"],
            "status": setup_payload["status"],
            "survey_id": setup_payload["survey_id"],
        }
        querystring = urlencode(get_ci_metadata_v2_payload)

        # sends request to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        query_ci_response_json = get_ci_metadata_v2_response.json()
        assert query_ci_response_json[0]["sds_schema"] == "xx-ytr-1234-856"

    def test_post_ci_with_same_metadata_query_ci_returns_with_description(self, setup_payload):
        # post 3 ci with the same data
        post_ci_v1(setup_payload)
        self.subscriber.pull_messages_and_acknowledge()
        get_ci_metadata_v2_payload = {
            "form_type": setup_payload["form_type"],
            "language": setup_payload["language"],
            "status": setup_payload["status"],
            "survey_id": setup_payload["survey_id"],
        }
        querystring = urlencode(get_ci_metadata_v2_payload)

        # sends request to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        query_ci_response_json = get_ci_metadata_v2_response.json()
        assert "description" in query_ci_response_json[0]
        assert query_ci_response_json[0]["description"] == setup_payload["description"]

    def test_metadata_query_returns_404(self, setup_payload):
        get_ci_metadata_v2_payload = {
            "form_type": setup_payload["form_type"],
            "language": setup_payload["language"],
            "status": setup_payload["status"],
            "survey_id": setup_payload["survey_id"],
        }
        querystring = urlencode(get_ci_metadata_v2_payload)

        # sends request to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        assert get_ci_metadata_v2_response.status_code == status.HTTP_404_NOT_FOUND
        query_ci_response = get_ci_metadata_v2_response.json()
        expected_response = f"No CI metadata found for: {get_ci_metadata_v2_payload}"
        assert query_ci_response["message"] == expected_response
        assert query_ci_response["status"] == "error"
