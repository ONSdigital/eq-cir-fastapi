from fastapi import status

from app.events.subscriber import Subscriber
from tests.integration_tests.utils import (
    delete_docs,
    get_ci_metadata_v2,
    post_ci_v1,
    put_status_v1,
)


class TestGetCiMetadataV2:
    subscriber = Subscriber()

    def teardown_method(self):
        print(": tearing down")
        delete_docs("3456")

    def test_post_3_ci_with_same_metadata_get_ci_metadata_v2_returns_3(self, setup_payload):
        for _ in range(3):
            post_ci_v1(setup_payload)
            self.subscriber.pull_messages_and_acknowledge()

        get_ci_metadata_v2_payload = {
            "form_type": setup_payload["form_type"],
            "language": setup_payload["language"],
            "survey_id": setup_payload["survey_id"],
        }

        # sends request to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_response = get_ci_metadata_v2(get_ci_metadata_v2_payload)
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

        # sends request to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_response = get_ci_metadata_v2(get_ci_metadata_v2_payload)
        get_ci_metadata_v2_response_data = get_ci_metadata_v2_response.json()
        ci_id = get_ci_metadata_v2_response_data[0]["id"]
        assert get_ci_metadata_v2_response_data[0]["status"] == "DRAFT"
        ci_update = put_status_v1(ci_id)
        assert ci_update.status_code == status.HTTP_200_OK
        # sends request to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_payload = {
            "form_type": setup_payload["form_type"],
            "language": setup_payload["language"],
            "status": "PUBLISHED",
            "survey_id": setup_payload["survey_id"],
        }
        get_ci_metadata_v2_post_response = get_ci_metadata_v2(get_ci_metadata_v2_payload)
        get_ci_metadata_v2_post_response_data = get_ci_metadata_v2_post_response.json()
        assert get_ci_metadata_v2_post_response_data[0]["status"] == "PUBLISHED"

    def test_get_ci_metadata_v2_returns_draft_and_put_ci_v1_returns_published(self, setup_payload):
        for _ in range(3):
            post_ci_v1(setup_payload)
            self.subscriber.pull_messages_and_acknowledge()

        # sends request, DRAFT only to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_response = get_ci_metadata_v2({"status": setup_payload["status"]})
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
        get_ci_metadata_v2_response = get_ci_metadata_v2(get_ci_metadata_v2_payload)
        get_ci_metadata_v2_response_data = get_ci_metadata_v2_response.json()
        ci_id = get_ci_metadata_v2_response_data[0]["id"]
        ci_update = put_status_v1(ci_id)
        assert ci_update.status_code == status.HTTP_200_OK
        # sends request, PUBLISHED only to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_post_response = get_ci_metadata_v2({"status": "PUBLISHED"})
        get_ci_metadata_v2_response_data = get_ci_metadata_v2_post_response.json()
        assert get_ci_metadata_v2_response_data[0]["status"] == "PUBLISHED"

    def test_get_ci_metadata_v2_returns_all_metadata(self):
        # Passing an empty list to the get_ci_metadata_v2
        get_ci_metadata_v2_response = get_ci_metadata_v2()
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
        # sends request to http_query_ci endpoint for data
        query_ci_response = get_ci_metadata_v2(get_ci_metadata_v2_payload)
        query_ci_response_json = query_ci_response.json()
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
        # sends request to http_query_ci endpoint for data
        query_ci_response = get_ci_metadata_v2(get_ci_metadata_v2_payload)
        query_ci_response_json = query_ci_response.json()
        assert "description" in query_ci_response[0]
        assert query_ci_response_json[0]["description"] == "Version of CI is for March 2023 - APPROVED"
