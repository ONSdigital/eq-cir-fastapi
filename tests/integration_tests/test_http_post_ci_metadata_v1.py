import json
from urllib.parse import urlencode

from fastapi import status

from app.events.subscriber import Subscriber
from app.models.responses import CiMetadata, CiStatus
from tests.integration_tests.utils import (
    make_iap_request,
    make_iap_request_with_unauthoried_id,
)


class TestPostCiV1:
    """Tests for the `http_post_ci_v1` endpoint."""

    post_url = "/v1/publish_collection_instrument"
    get_matadata_url = "/v1/ci_metadata"
    # Initialise the subscriber client
    subscriber = Subscriber()
    # NOTE: Anytime a happy path for post_ci_v1 is called, make sure to add in a line that pulls &
    # acknowledges the messages that are published to a topic

    def teardown_method(self):
        """
        This function deletes the test CI with survey_id:3456 at the end of each integration test to ensure it
        is not reflected in the firestore and schemas.
        """
        querystring = urlencode({"survey_id": 3456})
        make_iap_request("DELETE", f"/v1/dev/teardown?{querystring}")

    def test_can_publish_valid_ci(self, setup_payload):
        """
        What am I testing:
        AC-1.1 - The ability to submit a CI (well-formed) to the API endpoint,
        and the correct response is returned with the version.
        AC-1.3 - When a CI is published in the response the datetime
        field is present with an ISO8601 value. (2023-01-24T13:56:38Z)
        """
        # Creates a CI in the database, essentially running post_ci_v1 from handler folder
        ci_response = make_iap_request("POST", f"{self.post_url}", json=setup_payload)
        ci_response_data = ci_response.json()
        survey_id = setup_payload["survey_id"]
        form_type = setup_payload["form_type"]
        language = setup_payload["language"]

        querystring = urlencode({"form_type": form_type, "language": language, "survey_id": survey_id})
        # sends request to http_query_ci endpoint for data
        check_ci_in_db = make_iap_request("GET", f"{self.get_matadata_url}?{querystring}")
        check_ci_in_db_data = check_ci_in_db.json()

        received_messages = self.subscriber.pull_messages_and_acknowledge()

        decoded_received_messages = [x.decode("utf-8") for x in received_messages]
        decoded_received_messages = [json.loads(x) for x in decoded_received_messages]

        expected_ci = CiMetadata(
            ci_version=1,
            data_version=setup_payload["data_version"],
            form_type=setup_payload["form_type"],
            id=check_ci_in_db_data[0]["id"],
            language=setup_payload["language"],
            published_at=check_ci_in_db_data[0]["published_at"],
            schema_version=setup_payload["schema_version"],
            status=setup_payload["status"],
            survey_id=setup_payload["survey_id"],
            title=setup_payload["title"],
            description=setup_payload["description"],
        )

        assert "published_at" in ci_response_data
        assert ci_response_data["ci_version"] == 1
        # database assertion
        assert check_ci_in_db_data == [expected_ci.model_dump()]
        # assert that the metadata is pulled through in the subscription
        assert expected_ci.model_dump() in decoded_received_messages

    def test_can_publish_valid_ci_with_sds_schema(self, setup_payload):
        """
        What am I testing:
        AC-1.1 - The ability to submit a CI (well-formed) which has a sds_schema to the API endpoint,
        and the correct response is returned with the version.
        AC-1.3 - When a CI is published in the response the datetime
        field is present with an ISO8601 value. (2023-01-24T13:56:38Z)
        This test is very similar to test_can_publish_valid_ci expect that sds_schema value is not empty
        """
        # Creates a CI in the database, essentially running post_ci_v1 from handler folder
        setup_payload["sds_schema"] = "xx-ytr-1234-856"
        ci_response = make_iap_request("POST", f"{self.post_url}", json=setup_payload)
        ci_response_data = ci_response.json()

        survey_id = setup_payload["survey_id"]
        form_type = setup_payload["form_type"]
        language = setup_payload["language"]

        querystring = urlencode({"form_type": form_type, "language": language, "survey_id": survey_id})
        # sends request to http_query_ci endpoint for data
        check_ci_in_db = make_iap_request("GET", f"{self.get_matadata_url}?{querystring}")
        check_ci_in_db_data = check_ci_in_db.json()
        # Need to pull and acknowledge messages in any test where post_ci_v1 is called so the subscription doesn't get clogged
        received_messages = self.subscriber.pull_messages_and_acknowledge()

        decoded_received_messages = [x.decode("utf-8") for x in received_messages]
        decoded_received_messages = [json.loads(x) for x in decoded_received_messages]

        expected_ci = CiMetadata(
            ci_version=1,
            data_version=setup_payload["data_version"],
            form_type=setup_payload["form_type"],
            id=check_ci_in_db_data[0]["id"],
            language=setup_payload["language"],
            published_at=check_ci_in_db_data[0]["published_at"],
            schema_version=setup_payload["schema_version"],
            sds_schema=setup_payload["sds_schema"],
            status=setup_payload["status"],
            survey_id=setup_payload["survey_id"],
            title=setup_payload["title"],
            description=setup_payload["description"],
        )

        assert "published_at" in ci_response_data
        assert ci_response_data["ci_version"] == 1
        # database assertion
        assert check_ci_in_db_data == [expected_ci.model_dump()]
        # assert that the metadata is pulled through in the subscription
        assert expected_ci.model_dump() in decoded_received_messages

    def test_can_append_version_to_existing_ci(
        self,
        setup_publish_ci_return_payload,
    ):
        """
        What am I testing:
        Where the same CI is submitted(survey_id),
        then a new version is returned based on the survey_id
        """
        ci_response = make_iap_request("POST", f"{self.post_url}", json=setup_publish_ci_return_payload)
        ci_response_data = ci_response.json()

        # Need to pull and acknowledge messages in any test where post_ci_v1 is called so the subscription doesn't get clogged
        self.subscriber.pull_messages_and_acknowledge()

        survey_id = setup_publish_ci_return_payload["survey_id"]
        form_type = setup_publish_ci_return_payload["form_type"]
        language = setup_publish_ci_return_payload["language"]
        querystring = urlencode({"form_type": form_type, "language": language, "survey_id": survey_id})
        # sends request to http_query_ci endpoint for data
        check_ci_in_db = make_iap_request("GET", f"{self.get_matadata_url}?{querystring}")
        check_ci_in_db_data = check_ci_in_db.json()

        expected_ci = CiMetadata(
            ci_version=2,
            data_version=setup_publish_ci_return_payload["data_version"],
            form_type=setup_publish_ci_return_payload["form_type"],
            id=check_ci_in_db_data[0]["id"],
            language=setup_publish_ci_return_payload["language"],
            published_at=check_ci_in_db_data[0]["published_at"],
            schema_version=setup_publish_ci_return_payload["schema_version"],
            status=CiStatus.DRAFT.value,
            survey_id=setup_publish_ci_return_payload["survey_id"],
            title=setup_publish_ci_return_payload["title"],
            description=setup_publish_ci_return_payload["description"],
        )

        assert ci_response.status_code == status.HTTP_200_OK
        assert ci_response_data["ci_version"] == 2
        # database assertions
        assert len(check_ci_in_db_data) == 2
        assert check_ci_in_db_data[0] == expected_ci.model_dump()
        assert check_ci_in_db_data[1]["ci_version"] == 1
        assert check_ci_in_db_data[0]["ci_version"] == 2

    def test_cannot_publish_ci_missing_survey_id(
        self,
        setup_payload,
    ):
        """
        What am I testing:
            If a metadata field is missing <survey_id>, then the correct response is returned.
        """
        payload = setup_payload
        payload["survey_id"] = " "
        ci_response = make_iap_request("POST", f"{self.post_url}", json=payload)
        self.subscriber.pull_messages_and_acknowledge()

        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST

        ci_response_data = ci_response.json()
        assert ci_response_data == {
            "message": "Value error, survey_id can't be empty or null",
            "status": "error",
        }

    def test_cannot_publish_ci_missing_language(self, setup_payload):
        """
        What am I testing:
        AC-3.2	If a metadata field is missing <language>, then the correct response is returned.
        """
        payload = setup_payload
        payload["language"] = " "
        ci_response = make_iap_request("POST", f"{self.post_url}", json=payload)
        self.subscriber.pull_messages_and_acknowledge()

        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST

        ci_response_data = ci_response.json()
        assert ci_response_data == {
            "message": "Value error, language can't be empty or null",
            "status": "error",
        }

    def test_cannot_publish_ci_missing_form_type(self, setup_payload):
        """
        What am I testing:
        AC-3.3	If a metadata field is missing <form_type>, then the correct response is returned.
        """
        payload = setup_payload
        payload["form_type"] = " "
        ci_response = make_iap_request("POST", f"{self.post_url}", json=payload)
        self.subscriber.pull_messages_and_acknowledge()

        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST

        ci_response_data = ci_response.json()
        assert ci_response_data == {
            "message": "Value error, form_type can't be empty or null",
            "status": "error",
        }

    def test_cannot_publish_ci_missing_title(self, setup_payload):
        """
        What am I testing:
        AC-3.4	If a metadata field is missing <title>, then the correct response is returned.
        """
        payload = setup_payload
        payload["title"] = " "
        ci_response = make_iap_request("POST", f"{self.post_url}", json=payload)
        self.subscriber.pull_messages_and_acknowledge()

        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST

        ci_response_data = ci_response.json()
        assert ci_response_data == {
            "message": "Value error, title can't be empty or null",
            "status": "error",
        }

    def test_cannot_publish_ci_missing_schema_version(self, setup_payload):
        """
        What am I testing:
        AC-3.5	If a metadata field is missing <schema_version>, then the correct response is returned.
        """
        payload = setup_payload
        payload["schema_version"] = " "
        ci_response = make_iap_request("POST", f"{self.post_url}", json=payload)
        self.subscriber.pull_messages_and_acknowledge()

        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST

        ci_response_data = ci_response.json()
        assert ci_response_data == {
            "message": "Value error, schema_version can't be empty or null",
            "status": "error",
        }

    def test_cannot_publish_ci_missing_data_version(self, setup_payload):
        """
        What am I testing:
        AC-3.6	If a metadata field is missing <data_version>, then the correct response is returned.
        """
        payload = setup_payload
        payload["data_version"] = " "
        ci_response = make_iap_request("POST", f"{self.post_url}", json=payload)
        self.subscriber.pull_messages_and_acknowledge()

        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST

        ci_response_data = ci_response.json()
        assert ci_response_data == {
            "message": "Value error, data_version can't be empty or null",
            "status": "error",
        }

    def test_publish_ci_returns_unauthorized_request(self, setup_payload):
        """
        What am I testing:
        http_post_ci_metadata_v1 should return a 401 unauthorized error if the endpoint is
        requested with an unauthorized token.
        """
        payload = setup_payload
        ci_response = make_iap_request_with_unauthoried_id("POST", f"{self.post_url}", json=payload)

        assert ci_response.status_code == status.HTTP_401_UNAUTHORIZED
