from urllib.parse import urlencode, parse_qs

import pytest
from fastapi import status

from app.config import settings
from app.models.responses import CiMetadata
from app.services.ci_classifier_service import CiClassifierService
from tests.integration_tests.helpers.integration_helpers import subscriber_teardown, subscriber_setup, \
    generate_subscriber_id
from tests.integration_tests.helpers.pubsub_helper import PubSubHelper
from tests.integration_tests.utils import make_iap_request, create_post_params
from tests.test_config.endpoints import ENDPOINTS, POST_CI, GET_CI_METADATA, DELETE_CI
from tests.test_config.endpoints_loader import EndpointsLoader

ci_pubsub_helper = PubSubHelper(settings.PUBLISH_CI_TOPIC_ID)
endpoints_loader = EndpointsLoader(ENDPOINTS)


class TestPostCi:
    """
    Integration tests for the 'Post CI' endpoint.
    """

    post_url = endpoints_loader.get_url(POST_CI)
    encoded_list = create_post_params(3)

    get_metadata_url = endpoints_loader.get_url(GET_CI_METADATA)
    subscription_id = generate_subscriber_id()  # Unique subscription ID to avoid conflicts and GCP errors

    @classmethod
    def setup_class(cls) -> None:
        subscriber_setup(ci_pubsub_helper, cls.subscription_id)

    @classmethod
    def teardown_class(cls) -> None:
        subscriber_teardown(ci_pubsub_helper, cls.subscription_id)

    def teardown_method(self):
        """
        This function deletes the test CI with survey_id:3456 at the end of each integration test to ensure it
        is not reflected in the firestore and schemas.
        """
        querystring = urlencode({"survey_id": 3456})
        make_iap_request("DELETE", f"{endpoints_loader.get_url(DELETE_CI)}?{querystring}")

    def test_can_publish_valid_ci(self, setup_payload):
        """
        Test the 'Post CI' endpoint returns a 200 success status if a well-formed CI is submitted, and the correct response is returned
        - Post a CI using the 'Post CI' endpoint with all required fields and valid data
        - Assert that the response status code is 200 OK
        - Assert that the response body contains the expected data
        - Use the 'Get Ci Metadata V1' endpoint to retrieve the metadata for the posted CI using the same metadata
        - Assert that the response status code is 200 OK
        - Assert that the response body contains the expected metadata corresponding to the posted CI
        - Pull the message from the subscription and assert that the message matches the expected metadata for the posted CI
        """
        # create post parameters without assigning version number
        data = create_post_params(1)

        # call the post_ci endpoint with the setup_payload and post parameters
        ci_response = make_iap_request("POST", f"{self.post_url}?{data[0]}", json=setup_payload)

        # Assert response status code = 200 OK
        assert ci_response.status_code == status.HTTP_200_OK

        ci_response_data = ci_response.json()

        survey_id = setup_payload["survey_id"]
        classifier_type = CiClassifierService.get_classifier_type(setup_payload)
        classifier_value = CiClassifierService.get_classifier_value(setup_payload, classifier_type)
        language = setup_payload["language"]

        # Assert that the response body contains the expected data
        expected_ci_response_data = {
            "ci_version": 1,
            "classifier_type": classifier_type,
            "classifier_value": classifier_value,
            "data_version": setup_payload["data_version"],
            "guid": parse_qs(data[0])["guid"][0],
            "language": language,
            "published_at": ci_response_data["published_at"],
            "survey_id": survey_id,
            "title": setup_payload["title"],
            "validator_version": parse_qs(data[0])["validator_version"][0],
        }

        expected_ci_metadata = CiMetadata(**expected_ci_response_data)

        assert ci_response_data == expected_ci_response_data

        querystring = urlencode(
            {
                "classifier_type": classifier_type,
                "classifier_value": classifier_value,
                "language": language,
                "survey_id": survey_id,
            }
        )
        # sends request to http_query_ci endpoint for data
        get_metadata_response = make_iap_request("GET", f"{self.get_metadata_url}?{querystring}")

        # Assert response status code = 200 OK
        assert get_metadata_response.status_code == status.HTTP_200_OK
        get_metadata_response_data = get_metadata_response.json()

        # Assert that the response body contains the expected metadata
        assert get_metadata_response_data == [expected_ci_metadata.model_dump()]

        # Pull message from subscription
        received_messages = ci_pubsub_helper.try_pull_and_acknowledge_messages(self.subscription_id)

        # assert the pubsub message matches the expected metadata
        assert received_messages[0] == expected_ci_metadata.model_dump()

    def test_can_publish_valid_ci_with_sds_schema(self, setup_payload):
        """
        Test the 'Post CI' endpoint returns a 200 success status if a well-formed CI is submitted with sds_schema, and the correct response is returned
        - Post a CI using the 'Post CI' endpoint with all required fields and valid data, and with a valid sds_schema value
        - Assert that the response status code is 200 OK
        - Assert that the response body contains the expected data including the sds_schema value
        - Use the 'Get Ci Metadata V1' endpoint to retrieve the metadata for the posted CI using the same metadata
        - Assert that the response status code is 200 OK
        - Assert that the response body contains the expected metadata corresponding to the posted CI including the sds_schema value
        - Pull the message from the subscription and assert that the message matches the expected metadata for the posted CI including the sds_schema value
        """
        # create post parameters without assigning version number
        data = create_post_params(1)

        # create a copy of setup_payload and add sds_schema value to the copy of the payload
        new_payload = setup_payload.copy()
        new_payload["sds_schema"] = "xx-ytr-1234-856"

        # call the post_ci endpoint with the new_payload and post parameters
        ci_response = make_iap_request("POST", f"{self.post_url}?{data[0]}", json=new_payload)

        # Assert response status code = 200 OK
        assert ci_response.status_code == status.HTTP_200_OK

        ci_response_data = ci_response.json()
        survey_id = setup_payload["survey_id"]
        classifier_type = CiClassifierService.get_classifier_type(new_payload)
        classifier_value = CiClassifierService.get_classifier_value(new_payload, classifier_type)
        language = new_payload["language"]

        # Assert that the response body contains the expected data
        expected_ci_response_data = {
            "ci_version": 1,
            "classifier_type": classifier_type,
            "classifier_value": classifier_value,
            "data_version": new_payload["data_version"],
            "guid": parse_qs(data[0])["guid"][0],
            "language": language,
            "published_at": ci_response_data["published_at"],
            "survey_id": survey_id,
            "title": new_payload["title"],
            "validator_version": parse_qs(data[0])["validator_version"][0],
            "sds_schema": new_payload["sds_schema"],
        }

        expected_ci_metadata = CiMetadata(**expected_ci_response_data)

        assert ci_response_data == expected_ci_response_data

        querystring = urlencode(
            {
                "classifier_type": classifier_type,
                "classifier_value": classifier_value,
                "language": language,
                "survey_id": survey_id,
            }
        )
        # sends request to http_query_ci endpoint for data
        get_metadata_response = make_iap_request("GET", f"{self.get_metadata_url}?{querystring}")

        # Assert response status code = 200 OK
        assert get_metadata_response.status_code == status.HTTP_200_OK
        get_metadata_response_data = get_metadata_response.json()

        # Assert that the response body contains the expected metadata
        assert get_metadata_response_data == [expected_ci_metadata.model_dump()]

        # Pull message from subscription
        received_messages = ci_pubsub_helper.try_pull_and_acknowledge_messages(self.subscription_id)

        # assert the pubsub message matches the expected metadata
        assert received_messages[0] == expected_ci_metadata.model_dump()

    def test_can_append_version_to_existing_ci(
            self,
            setup_payload,
    ):
        """
        Test the 'Post CI' endpoint can append a new version to an existing CI when a new CI is posted with the same metadata
        - Post a CI using the 'Post CI' endpoint with all required fields and valid data
        - Post another CI with the same metadata and validator version, but different guid
        - Assert that both CIs are stored in the database with the correct version numbers (the second CI should have a version number that is incremented by 1 from the first CI)
        - Use the 'Get Ci Metadata V1' endpoint to retrieve the metadata for the posted CIs using the same metadata
        - Assert that the response status code is 200 OK
        - Assert that the response body contains the expected metadata for both CIs with correct version numbers
        """
        # create post parameters without assigning version number
        data = create_post_params(2)

        # call the post_ci endpoint with the setup_payload and post parameters twice to create two versions of the same CI
        for d in data:
            ci_response = make_iap_request("POST", f"{self.post_url}?{d}", json=setup_payload)
            assert ci_response.status_code == status.HTTP_200_OK

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
        get_metadata_response = make_iap_request("GET", f"{self.get_metadata_url}?{querystring}")

        assert get_metadata_response.status_code == status.HTTP_200_OK
        get_metadata_response_data = get_metadata_response.json()

        expected_ci_metadata_list = [
            CiMetadata(
                ci_version=2,
                validator_version=parse_qs(data[1])["validator_version"][0],
                data_version=setup_payload["data_version"],
                classifier_type=classifier_type,
                classifier_value=classifier_value,
                guid=parse_qs(data[1])["guid"][0],
                language=setup_payload["language"],
                published_at=get_metadata_response_data[0]["published_at"],
                survey_id=setup_payload["survey_id"],
                title=setup_payload["title"],
            ),
            CiMetadata(
                ci_version=1,
                validator_version=parse_qs(data[0])["validator_version"][0],
                data_version=setup_payload["data_version"],
                classifier_type=classifier_type,
                classifier_value=classifier_value,
                guid=parse_qs(data[0])["guid"][0],
                language=setup_payload["language"],
                published_at=get_metadata_response_data[1]["published_at"],
                survey_id=setup_payload["survey_id"],
                title=setup_payload["title"],
            )
        ]

        # database assertions
        assert len(get_metadata_response_data) == 2
        assert get_metadata_response_data == [ci_metadata.model_dump() for ci_metadata in expected_ci_metadata_list]

        # Need to pull and acknowledge messages to clear subscription
        ci_pubsub_helper.try_pull_and_acknowledge_messages(self.subscription_id)

    def test_can_post_ci_with_assigned_version_number(
            self,
            setup_payload
    ):
        """
        Test the 'Post CI' endpoint can accept a CI with an assigned version number and store it in the database with the assigned version number
        - Post a CI using the 'Post CI' endpoint with all required fields and valid data, and with an assigned version number in the post parameters
        - Post another CI with the same metadata and validator version, but different guid and assigned version number in the post parameters
        - Use the 'Get Ci Metadata V1' endpoint to retrieve the metadata for the posted CIs using the same metadata
        - Assert that the response status code is 200 OK
        - Assert that the response body contains the expected metadata for both CIs with the assigned version numbers from the post parameters, not auto-incremented version numbers
        """
        # create post parameters with assigned version number
        data = create_post_params(2, validator_version="0.0.2", with_version=True)

        # call the post_ci endpoint with the setup_payload and post parameters to create two CIs with assigned version numbers
        for d in data:
            ci_response = make_iap_request("POST", f"{self.post_url}?{d}", json=setup_payload)
            assert ci_response.status_code == status.HTTP_200_OK

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
        get_metadata_response = make_iap_request("GET", f"{self.get_metadata_url}?{querystring}")

        assert get_metadata_response.status_code == status.HTTP_200_OK
        get_metadata_response_data = get_metadata_response.json()

        # The expected metadata list should reflect the version numbers assigned in the post parameters, not auto-incremented version numbers
        expected_ci_metadata_list = [
            CiMetadata(
                ci_version=parse_qs(data[1])["ci_version"][0],
                validator_version=parse_qs(data[1])["validator_version"][0],
                data_version=setup_payload["data_version"],
                classifier_type=classifier_type,
                classifier_value=classifier_value,
                guid=parse_qs(data[1])["guid"][0],
                language=setup_payload["language"],
                published_at=get_metadata_response_data[0]["published_at"],
                survey_id=setup_payload["survey_id"],
                title=setup_payload["title"],
            ),
            CiMetadata(
                ci_version=parse_qs(data[0])["ci_version"][0],
                validator_version=parse_qs(data[0])["validator_version"][0],
                data_version=setup_payload["data_version"],
                classifier_type=classifier_type,
                classifier_value=classifier_value,
                guid=parse_qs(data[0])["guid"][0],
                language=setup_payload["language"],
                published_at=get_metadata_response_data[1]["published_at"],
                survey_id=setup_payload["survey_id"],
                title=setup_payload["title"],
            )
        ]

        # database assertions
        assert len(get_metadata_response_data) == 2
        assert get_metadata_response_data == [ci_metadata.model_dump() for ci_metadata in expected_ci_metadata_list]

        # Need to pull and acknowledge messages to clear subscription
        ci_pubsub_helper.try_pull_and_acknowledge_messages(self.subscription_id)

    def test_cannot_publish_ci_with_same_guid(
            self,
            setup_payload
    ):
        """
        Test the 'Post CI' endpoint returns a 400 bad request status if a CI is submitted with the same guid as an existing CI, and the correct response is returned
        - Post a CI using the 'Post CI' endpoint with all required fields and valid data
        - Post another CI with the same guid in the post parameters as the first CI
        - Assert that the response status code is 400 Bad Request and the correct error message is returned indicating invalid guid
        """
        # create post parameters without assigning version number
        data = create_post_params(1)

        # call the post_ci endpoint with the setup_payload and post parameters to create a CI
        ci_response = make_iap_request("POST", f"{self.post_url}?{data[0]}", json=setup_payload)

        # Assert response status code = 200 OK
        assert ci_response.status_code == status.HTTP_200_OK

        # call the post_ci endpoint again with the same guid in the post parameters to create another CI
        ci_response = make_iap_request("POST", f"{self.post_url}?{data[0]}", json=setup_payload)

        # Assert response status code = 400 Bad Request and the correct error message is returned
        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST
        assert ci_response.json()["message"] == "Invalid GUID provided"

    def test_cannot_publish_ci_with_version_smaller_than_latest_version(
            self,
            setup_payload
    ):
        """
        Test the 'Post CI' endpoint returns a 400 bad request status if a CI is submitted with an assigned version number that is smaller than the latest version number for the same metadata, and the correct response is returned
        - Post a CI using the 'Post CI' endpoint with all required fields and assign with version number 3
        - Post another CI with the same metadata and validator version, but different guid and with an assigned version number smaller than previous version number
        - Assert that the response status code is 400 Bad Request and the correct error message is returned indicating invalid ci_version
        """
        # create post parameters with assigned version number
        data = create_post_params(3, validator_version="0.0.3", with_version=True)

        # call the post_ci endpoint with the setup_payload and post parameters to create a CI with version 3
        ci_response = make_iap_request("POST", f"{self.post_url}?{data[2]}", json=setup_payload)

        # Assert response status code = 200 OK
        assert ci_response.status_code == status.HTTP_200_OK

        # call the post_ci endpoint again with the same metadata but with version 2 which is smaller than the latest version 3
        ci_response = make_iap_request("POST", f"{self.post_url}?{data[1]}", json=setup_payload)

        # Assert response status code = 400 Bad Request and the correct error message is returned
        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST
        assert ci_response.json()["message"] == "Invalid ci_version provided"

    def test_cannot_publish_ci_without_validator_version(
            self,
            setup_payload
    ):
        """
        Test the 'Post CI' endpoint returns a 400 bad request status if a CI is submitted without a validator version in the post parameters, and the correct response is returned
        - Post a CI using the 'Post CI' endpoint with all required fields and valid data, but without a validator version in the post parameters
        - Assert that the response status code is 400 Bad Request and the correct error message is returned indicating no validator version provided
        """
        # call the post_ci endpoint with the setup_payload and post parameters without validator version
        ci_response = make_iap_request("POST", f"{self.post_url}?guid=test-guid-001", json=setup_payload)

        # Assert response status code = 400 Bad Request and the correct error message is returned
        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST
        assert ci_response.json()["message"] == "No validator version provided"

    def test_cannot_publish_ci_without_guid(
            self,
            setup_payload
    ):
        """
        Test the 'Post CI' endpoint returns a 400 bad request status if a CI is submitted without a guid in the post parameters, and the correct response is returned
        - Post a CI using the 'Post CI' endpoint with all required fields and valid data, but without a guid in the post parameters
        - Assert that the response status code is 400 Bad Request and the correct error message is returned indicating no guid provided
        """
        # call the post_ci endpoint with the setup_payload and post parameters without guid
        ci_response = make_iap_request("POST", f"{self.post_url}?validator_version=0.0.1", json=setup_payload)

        # Assert response status code = 400 Bad Request and the correct error message is returned
        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST
        assert ci_response.json()["message"] == "Invalid GUID provided"

    def test_cannot_publish_ci_missing_survey_id(
            self,
            setup_payload,
    ):
        """
        Test the 'Post CI' endpoint returns a 400 bad request status if a CI is submitted with missing survey_id, and the correct response is returned
        - Post a CI using the 'Post CI' endpoint with all required fields and valid data except with a missing survey_id value
        - Assert that the response status code is 400 Bad Request
        - Assert that the response body contains the expected error message indicating validation failure due to missing survey_id
        """
        new_payload = setup_payload.copy()
        new_payload["survey_id"] = " "

        data = create_post_params(1)
        ci_response = make_iap_request("POST", f"{self.post_url}?{data[0]}", json=new_payload)

        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST

        ci_response_data = ci_response.json()
        assert ci_response_data == {
            "message": "Validation has failed",
            "status": "error",
        }

    def test_cannot_publish_ci_missing_language(self, setup_payload):
        """
        Test the 'Post CI' endpoint returns a 400 bad request status if a CI is submitted with missing language, and the correct response is returned
        - Post a CI using the 'Post CI' endpoint with all required fields and valid data except with a missing language value
        - Assert that the response status code is 400 Bad Request
        - Assert that the response body contains the expected error message indicating validation failure due to missing language
        """
        new_payload = setup_payload.copy()
        new_payload["language"] = " "

        data = create_post_params(1)
        ci_response = make_iap_request("POST", f"{self.post_url}?{data[0]}", json=new_payload)

        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST

        ci_response_data = ci_response.json()
        assert ci_response_data == {
            "message": "Validation has failed",
            "status": "error",
        }

    def test_cannot_publish_ci_missing_classifier_type(self, setup_payload):
        """
        Test the 'Post CI' endpoint returns a 400 bad request status if a CI is submitted with missing classifier type, and the correct response is returned
        - Post a CI using the 'Post CI' endpoint with all required fields and valid data except with a missing classifier type value
        - Assert that the response status code is 400 Bad Request
        - Assert that the response body contains the expected error message indicating invalid classifier due to missing classifier type
        """
        new_payload = setup_payload.copy()
        classifier_type = CiClassifierService.get_classifier_type(new_payload)
        new_payload.pop(classifier_type)

        data = create_post_params(1)
        ci_response = make_iap_request("POST", f"{self.post_url}?{data[0]}", json=new_payload)

        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST

        ci_response_data = ci_response.json()
        assert ci_response_data == {
            "message": "Invalid classifier",
            "status": "error",
        }

    def test_cannot_publish_ci_missing_title(self, setup_payload):
        """
        Test the 'Post CI' endpoint returns a 400 bad request status if a CI is submitted with missing title, and the correct response is returned
        - Post a CI using the 'Post CI' endpoint with all required fields and valid data except with a missing title value
        - Assert that the response status code is 400 Bad Request
        - Assert that the response body contains the expected error message indicating validation failure due to missing title
        """
        new_payload = setup_payload.copy()
        new_payload["title"] = " "

        data = create_post_params(1)
        ci_response = make_iap_request("POST", f"{self.post_url}?{data[0]}", json=new_payload)

        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST

        ci_response_data = ci_response.json()
        assert ci_response_data == {
            "message": "Validation has failed",
            "status": "error",
        }

    def test_cannot_publish_ci_missing_data_version(self, setup_payload):
        """
        Test the 'Post CI' endpoint returns a 400 bad request status if a CI is submitted with missing data_version, and the correct response is returned
        - Post a CI using the 'Post CI' endpoint with all required fields and valid data except with a missing data_version value
        - Assert that the response status code is 400 Bad Request
        - Assert that the response body contains the expected error message indicating validation failure due to missing data_version
        """
        new_payload = setup_payload.copy()
        new_payload["data_version"] = " "

        data = create_post_params(1)
        ci_response = make_iap_request("POST", f"{self.post_url}?{data[0]}", json=new_payload)

        assert ci_response.status_code == status.HTTP_400_BAD_REQUEST

        ci_response_data = ci_response.json()
        assert ci_response_data == {
            "message": "Validation has failed",
            "status": "error",
        }

    def test_publish_ci_returns_unauthorized_request(self, setup_payload):
        """
        Test the 'Post CI' endpoint returns a 401 unauthorized status if a CI is submitted without valid authentication, and the correct response is returned
        - Post a CI using the 'Post CI' endpoint with all required fields and valid data, but with an unauthenticated request
        - Assert that the response status code is 401 Unauthorized
        """
        if settings.CONF == "local-int-tests":
            pytest.skip("Skipping test_publish_ci_returns_unauthorized_request on local environment")

        data = create_post_params(1)

        ci_response = make_iap_request("POST", f"{self.post_url}?{data[0]}", json=setup_payload, unauthenticated=True)

        assert ci_response.status_code == status.HTTP_401_UNAUTHORIZED