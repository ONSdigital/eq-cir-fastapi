from fastapi import status

from app.events.subscriber import Subscriber
from tests.integration_tests.utils import (
    delete_docs,
    get_ci_metadata_v1,
    get_ci_schema_v2,
    post_ci_v1,
)


class TestGetCiSchemaV2:
    subscriber = Subscriber()

    def teardown_method(self):
        print(": tearing down")
        delete_docs("3456")

    def test_get_ci_schema_v2_returns_400(self):
        guid = "30134e70-c28c-4dcc-b0b0-e403b2df0b24"
        get_ci_schema_v2_response = get_ci_schema_v2(guid)
        get_ci_schema_v2_response = get_ci_schema_v2_response.json()
        get_ci_schema_v2_response["status"] == "error"
        get_ci_schema_v2_response["message"] == "No CI found for " + guid

    def test_publish_1_ci_get_ci_schema_v2_returns_1(self, setup_payload):
        # post ci
        post_ci_v1(setup_payload)
        self.subscriber.pull_messages_and_acknowledge()
        # Getting the ID of the CI
        survey_id = setup_payload["survey_id"]
        form_type = setup_payload["form_type"]
        language = setup_payload["language"]
        # sends request to http_query_ci endpoint for data
        get_ci_metadata_v1_response = get_ci_metadata_v1(survey_id, form_type, language)
        get_ci_metadata_v1_response = get_ci_metadata_v1_response.json()
        # sends request to http_get_ci_schema_v2 endpoint for data
        get_ci_schema_v2_response = get_ci_schema_v2(get_ci_metadata_v1_response[0]["id"])
        get_ci_schema_v2_response_data = get_ci_schema_v2_response.json()
        assert get_ci_schema_v2_response.status_code == status.HTTP_200_OK
        assert get_ci_schema_v2_response_data["survey_id"] == get_ci_metadata_v1_response[0]["survey_id"]
        assert get_ci_schema_v2_response_data["form_type"] == get_ci_metadata_v1_response[0]["form_type"]
        assert get_ci_schema_v2_response_data["language"] == get_ci_metadata_v1_response[0]["language"]
