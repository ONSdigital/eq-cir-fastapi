from urllib.parse import urlencode

from fastapi import status

from app.events.subscriber import Subscriber
from tests.integration_tests.utils import make_iap_request


class TestGetCiMetadataV1:
    base_url = "/v1/ci_metadata"
    subscriber = Subscriber()

    def teardown_method(self):
        print(": tearing down")
        querystring = urlencode({"survey_id": 3456})
        make_iap_request("DELETE", f"/v1/dev/teardown?{querystring}")

    def test_post_3_ci_with_same_metadata_query_ci_returns_3(self, setup_payload):
        # post 3 ci with the same data
        for _ in range(3):
            make_iap_request("POST", "/v1/publish_collection_instrument", json=setup_payload)
            self.subscriber.pull_messages_and_acknowledge()

        survey_id = setup_payload["survey_id"]
        form_type = setup_payload["form_type"]
        language = setup_payload["language"]
        querystring = urlencode({"form_type": form_type, "language": language, "survey_id": survey_id})
        # sends request to http_query_ci endpoint for data
        query_ci_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        query_ci_response_data = query_ci_response.json()

        assert len(query_ci_response_data) == 3
        assert query_ci_response_data[2]["ci_version"] == 1
        assert query_ci_response_data[1]["ci_version"] == 2
        assert query_ci_response_data[0]["ci_version"] == 3

    def test_post_ci_with_different_language_only_returns_1(self, setup_payload):
        # post 3 ci with the same data
        for _ in range(3):
            make_iap_request("POST", "/v1/publish_collection_instrument", json=setup_payload)
            self.subscriber.pull_messages_and_acknowledge()

        survey_id = setup_payload["survey_id"]
        form_type = setup_payload["form_type"]
        language = setup_payload["language"]
        querystring = urlencode({"form_type": form_type, "language": language, "survey_id": survey_id})
        # sends request to http_query_ci endpoint for data
        query_ci_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        query_ci_response_data = query_ci_response.json()

        setup_payload["language"] = "English"
        make_iap_request("POST", "/v1/publish_collection_instrument", json=setup_payload)
        querystring = urlencode({"form_type": form_type, "language": "English", "survey_id": survey_id})
        # sends request to http_query_ci endpoint for data
        new_language_query_ci_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        new_language_query_ci_response_data = new_language_query_ci_response.json()

        assert len(query_ci_response_data) == 3
        assert len(new_language_query_ci_response_data) == 1
        assert new_language_query_ci_response_data[0]["language"] == "English"

    def test_post_ci_with_same_metadata_query_ci_returns_with_sds_schema(self, setup_payload):
        # post 3 ci with the same data
        setup_payload["sds_schema"] = "xx-ytr-1234-856"
        make_iap_request("POST", "/v1/publish_collection_instrument", json=setup_payload)
        self.subscriber.pull_messages_and_acknowledge()

        survey_id = setup_payload["survey_id"]
        form_type = setup_payload["form_type"]
        language = setup_payload["language"]
        querystring = urlencode({"form_type": form_type, "language": language, "survey_id": survey_id})
        # sends request to http_query_ci endpoint for data
        query_ci_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        query_ci_response_json = query_ci_response.json()
        assert query_ci_response_json[0]["sds_schema"] == "xx-ytr-1234-856"

    def test_post_ci_with_same_metadata_query_ci_returns_with_description(self, setup_payload):
        # post 3 ci with the same data
        make_iap_request("POST", "/v1/publish_collection_instrument", json=setup_payload)
        self.subscriber.pull_messages_and_acknowledge()

        survey_id = setup_payload["survey_id"]
        form_type = setup_payload["form_type"]
        language = setup_payload["language"]
        querystring = urlencode({"form_type": form_type, "language": language, "survey_id": survey_id})
        # sends request to http_query_ci endpoint for data
        query_ci_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        query_ci_response_json = query_ci_response.json()
        assert "description" in query_ci_response_json[0]
        assert query_ci_response_json[0]["description"] == setup_payload["description"]

    def test_metadata_query_ci_returns_404(self, setup_payload):
        survey_id = setup_payload["survey_id"]
        form_type = setup_payload["form_type"]
        language = setup_payload["language"]
        querystring = urlencode({"form_type": form_type, "language": language, "survey_id": survey_id})
        # sends request to http_query_ci endpoint for data
        query_ci_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        assert query_ci_response.status_code == status.HTTP_404_NOT_FOUND
        query_ci_response = query_ci_response.json()
        expected_response = (
            f"No CI metadata found for: {{'form_type': '{form_type}', 'language': '{language}', 'survey_id': '{survey_id}'}}"
        )
        assert query_ci_response["message"] == expected_response
        assert query_ci_response["status"] == "error"

    def test_metadata_query_ci_returns_400(self, setup_payload):
        """
        A 400 error can be thrown if arguments/syntactic rules are against the defined endpoint.
        In this test only two endpoints are passed instead of three.
        make_iap_request is used instead of get_ci_metadata_v1 here as this function defined in utils.py takes in the
        three required parameters. Using make_iap_request can enable us to throw 400 error.
        """
        survey_id = setup_payload["survey_id"]
        form_type = setup_payload["form_type"]
        querystring = urlencode({"survey_id": survey_id, "form_type": form_type})
        response = make_iap_request("GET", f"/v1/ci_metadata?{querystring}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
