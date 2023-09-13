from fastapi import status
from urllib.parse import urlencode
from tests.integration_tests.utils import make_iap_request


from app.events.subscriber import Subscriber
from tests.integration_tests.utils import delete_docs, get_ci_metadata_v1, post_ci_v1


class TestGetCiMetadataV1:
    subscriber = Subscriber()

    def teardown_method(self):
        print(": tearing down")
        delete_docs("3456")

    def test_post_3_ci_with_same_metadata_query_ci_returns_3(self, setup_payload):
        # post 3 ci with the same data
        for _ in range(3):
            post_ci_v1(setup_payload)
            self.subscriber.pull_messages_and_acknowledge()

        survey_id = setup_payload["survey_id"]
        form_type = setup_payload["form_type"]
        language = setup_payload["language"]
        # sends request to http_query_ci endpoint for data
        query_ci_response = get_ci_metadata_v1(survey_id, form_type, language)
        query_ci_response_data = query_ci_response.json()

        assert len(query_ci_response_data) == 3
        assert query_ci_response_data[2]["ci_version"] == 1
        assert query_ci_response_data[1]["ci_version"] == 2
        assert query_ci_response_data[0]["ci_version"] == 3

    def test_post_ci_with_different_language_only_returns_1(self, setup_payload):
        # post 3 ci with the same data
        for _ in range(3):
            post_ci_v1(setup_payload)
            self.subscriber.pull_messages_and_acknowledge()

        survey_id = setup_payload["survey_id"]
        form_type = setup_payload["form_type"]
        language = setup_payload["language"]
        # sends request to http_query_ci endpoint for data
        query_ci_response = get_ci_metadata_v1(survey_id, form_type, language)
        query_ci_response_data = query_ci_response.json()

        setup_payload["language"] = "English"
        post_ci_v1(setup_payload)
        new_language_query_ci_response = get_ci_metadata_v1(survey_id, form_type, "English")
        new_language_query_ci_response_data = new_language_query_ci_response.json()

        assert len(query_ci_response_data) == 3
        assert len(new_language_query_ci_response_data) == 1
        assert new_language_query_ci_response_data[0]["language"] == "English"

    def test_post_ci_with_same_metadata_query_ci_returns_with_sds_schema(self, setup_payload):
        # post 3 ci with the same data
        setup_payload["sds_schema"] = "xx-ytr-1234-856"
        post_ci_v1(setup_payload)
        self.subscriber.pull_messages_and_acknowledge()

        survey_id = setup_payload["survey_id"]
        form_type = setup_payload["form_type"]
        language = setup_payload["language"]
        # sends request to http_query_ci endpoint for data
        query_ci_response = get_ci_metadata_v1(survey_id, form_type, language)
        query_ci_response_json = query_ci_response.json()
        assert query_ci_response_json[0]["sds_schema"] == "xx-ytr-1234-856"

    def test_post_ci_with_same_metadata_query_ci_returns_with_description(self, setup_payload):
        # post 3 ci with the same data
        post_ci_v1(setup_payload)
        self.subscriber.pull_messages_and_acknowledge()

        survey_id = setup_payload["survey_id"]
        form_type = setup_payload["form_type"]
        language = setup_payload["language"]
        # sends request to http_query_ci endpoint for data
        query_ci_response = get_ci_metadata_v1(survey_id, form_type, language)
        query_ci_response_json = query_ci_response.json()
        assert "description" in query_ci_response_json[0]
        assert query_ci_response_json[0]["description"] == setup_payload["description"]

    def test_metadata_query_ci_returns_404(self, setup_payload):
        delete_docs("3456")
        survey_id = setup_payload["survey_id"]
        form_type = setup_payload["form_type"]
        language = setup_payload["language"]
        # sends request to http_query_ci endpoint for data
        query_ci_response = get_ci_metadata_v1(survey_id, form_type, language)
        query_ci_response.status_code == status.HTTP_404_NOT_FOUND
        query_ci_response = query_ci_response.json()
        assert (
            query_ci_response["message"]
            == f"No CI metadata found for: {{'survey_id': '{survey_id}', 'form_type: '{form_type}', 'language': '{language}'}}"
        )
        assert query_ci_response["status"] == "error"

    def test_metadata_query_ci_returns_400(self, setup_payload):
        survey_id = setup_payload["survey_id"]
        form_type = setup_payload["form_type"]
        querystring = urlencode({"survey_id": survey_id,"form_type":form_type})

        response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

