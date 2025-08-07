from urllib.parse import urlencode

import pytest
from fastapi import status

from app.config import settings
from tests.integration_tests.helpers.integration_helpers import pubsub_setup, pubsub_teardown, inject_wait_time
from tests.integration_tests.helpers.pubsub_helper import ci_pubsub_helper
from app.models.responses import CiMetadata
from app.services.ci_classifier_service import CiClassifierService
from tests.integration_tests.utils import make_iap_request


class TestPostCiV1:
    """Tests for the `http_post_ci_v1` endpoint."""

    post_url = "/v1/publish_collection_instrument"
    get_matadata_url = "/v1/ci_metadata"

    # NOTE: Anytime a happy path for post_ci_v1 is called, make sure to add in a line that pulls &
    # acknowledges the messages that are published to a topic

    @classmethod
    def setup_class(cls) -> None:
        pubsub_setup(ci_pubsub_helper, settings.SUBSCRIPTION_ID)
        inject_wait_time(3)  # Allow pubsub topic to be created

    @classmethod
    def teardown_class(cls) -> None:
        inject_wait_time(3)  # Allow time for messages to be pulled
        pubsub_teardown(ci_pubsub_helper, settings.SUBSCRIPTION_ID)
        inject_wait_time(3)  # Allow pubsub subscription to be deleted (subscription lingers after 200 response)

    def teardown_method(self):
        """
        This function deletes the test CI with survey_id:3456 at the end of each integration test to ensure it
        is not reflected in the firestore and schemas.
        """
        querystring = urlencode({"survey_id": 3456})
        make_iap_request("DELETE", f"/v1/dev/teardown?{querystring}")
        # pubsub_purge_messages(ci_pubsub_helper, settings.SUBSCRIPTION_ID)

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
        classifier_type = CiClassifierService.get_classifier_type(setup_payload)
        classifier_value = CiClassifierService.get_classifier_value(setup_payload, classifier_type)
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
        check_ci_in_db = make_iap_request("GET", f"{self.get_matadata_url}?{querystring}")
        check_ci_in_db_data = check_ci_in_db.json()

        received_messages = ci_pubsub_helper.pull_and_acknowledge_messages(settings.SUBSCRIPTION_ID)

        expected_ci = CiMetadata(
            ci_version=1,
            data_version=setup_payload["data_version"],
            validator_version="",
            classifier_type=classifier_type,
            classifier_value=classifier_value,
            guid=check_ci_in_db_data[0]["guid"],
            language=setup_payload["language"],
            published_at=check_ci_in_db_data[0]["published_at"],
            survey_id=setup_payload["survey_id"],
            title=setup_payload["title"],
        )

        assert "published_at" in ci_response_data
        assert ci_response_data["ci_version"] == 1
        # database assertion
        assert check_ci_in_db_data == [expected_ci.model_dump()]
        # assert that the metadata is pulled through in the subscription
        assert expected_ci.model_dump() == received_messages[0]

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
        classifier_type = CiClassifierService.get_classifier_type(setup_payload)
        classifier_value = CiClassifierService.get_classifier_value(setup_payload, classifier_type)
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
        check_ci_in_db = make_iap_request("GET", f"{self.get_matadata_url}?{querystring}")
        check_ci_in_db_data = check_ci_in_db.json()

        received_messages = ci_pubsub_helper.pull_and_acknowledge_messages(settings.SUBSCRIPTION_ID)

        expected_ci = CiMetadata(
            ci_version=1,
            data_version=setup_payload["data_version"],
            validator_version="",
            classifier_type=classifier_type,
            classifier_value=classifier_value,
            guid=check_ci_in_db_data[0]["guid"],
            language=setup_payload["language"],
            published_at=check_ci_in_db_data[0]["published_at"],
            sds_schema=setup_payload["sds_schema"],
            survey_id=setup_payload["survey_id"],
            title=setup_payload["title"],
        )

        assert "published_at" in ci_response_data
        assert ci_response_data["ci_version"] == 1
        # database assertion
        assert check_ci_in_db_data == [expected_ci.model_dump()]
        # assert that the metadata is pulled through in the subscription
        assert expected_ci.model_dump() == received_messages[0]

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

        survey_id = setup_publish_ci_return_payload["survey_id"]
        classifier_type = CiClassifierService.get_classifier_type(setup_publish_ci_return_payload)
        classifier_value = CiClassifierService.get_classifier_value(setup_publish_ci_return_payload, classifier_type)
        language = setup_publish_ci_return_payload["language"]
        querystring = urlencode(
            {
                "classifier_type": classifier_type,
                "classifier_value": classifier_value,
                "language": language,
                "survey_id": survey_id,
            }
        )
        # sends request to http_query_ci endpoint for data
        check_ci_in_db = make_iap_request("GET", f"{self.get_matadata_url}?{querystring}")
        check_ci_in_db_data = check_ci_in_db.json()

        expected_ci = CiMetadata(
            ci_version=2,
            validator_version="",
            data_version=setup_publish_ci_return_payload["data_version"],
            classifier_type=classifier_type,
            classifier_value=classifier_value,
            guid=check_ci_in_db_data[0]["guid"],
            language=setup_publish_ci_return_payload["language"],
            published_at=check_ci_in_db_data[0]["published_at"],
            survey_id=setup_publish_ci_return_payload["survey_id"],
            title=setup_publish_ci_return_payload["title"],
        )

        assert ci_response.status_code == status.HTTP_200_OK
        assert ci_response_data["ci_version"] == 2
        # database assertions
        assert len(check_ci_in_db_data) == 2
        assert check_ci_in_db_data[0] == expected_ci.model_dump()
        assert check_ci_in_db_data[1]["ci_version"] == 1
        assert check_ci_in_db_data[0]["ci_version"] == 2

        ci_pubsub_helper.pull_and_acknowledge_messages(settings.SUBSCRIPTION_ID)

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

        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST

        ci_response_data = ci_response.json()
        assert ci_response_data == {
            "message": "Validation has failed",
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

        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST

        ci_response_data = ci_response.json()
        assert ci_response_data == {
            "message": "Validation has failed",
            "status": "error",
        }

    def test_cannot_publish_ci_missing_classifier_type(self, setup_payload):
        """
        What am I testing:
        AC-3.3	If a metadata field is missing a classifier, then the correct response is returned.
        """
        payload = setup_payload
        classifier_type = CiClassifierService.get_classifier_type(payload)
        payload.pop(classifier_type)

        ci_response = make_iap_request("POST", f"{self.post_url}", json=payload)

        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST

        ci_response_data = ci_response.json()
        assert ci_response_data == {
            "message": "Invalid classifier",
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

        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST

        ci_response_data = ci_response.json()
        assert ci_response_data == {
            "message": "Validation has failed",
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

        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST

        ci_response_data = ci_response.json()
        assert ci_response_data == {
            "message": "Validation has failed",
            "status": "error",
        }

    def test_publish_ci_returns_unauthorized_request(self, setup_payload):
        """
        What am I testing:
        http_post_ci_metadata_v1 should return a 401 unauthorized error if the endpoint is
        requested with an unauthorized token.
        """
        if settings.CONF == "local-int-tests":
            pytest.skip("Skipping test_publish_ci_returns_unauthorized_request on local environment")

        payload = setup_payload
        ci_response = make_iap_request("POST", f"{self.post_url}", json=payload, unauthenticated=True)

        assert ci_response.status_code == status.HTTP_401_UNAUTHORIZED
