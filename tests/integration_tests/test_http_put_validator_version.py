from urllib.parse import urlencode, parse_qs

from starlette import status

from app.models.requests import UpdateValidatorVersionV1Params, PostCiSchemaV1Data
from app.models.responses import CiMetadata
from app.services.ci_classifier_service import CiClassifierService
from tests.integration_tests.utils import make_iap_request, create_post_params
from tests.test_config.endpoints import ENDPOINTS, PUT_VALIDATOR_VERSION, GET_CI_METADATA_V1, POST_CI, DELETE_CI, \
    GET_CI_SCHEMA
from tests.test_config.endpoints_loader import EndpointsLoader

endpoints_loader = EndpointsLoader(ENDPOINTS)


class TestPutValidatorVersion:
    """
    Integration tests for the 'Put Validator Version' endpoint.
    """
    post_url = endpoints_loader.get_url(POST_CI)
    update_validator = endpoints_loader.get_url(PUT_VALIDATOR_VERSION)
    get_metadata_url = endpoints_loader.get_url(GET_CI_METADATA_V1)
    get_schema_url = endpoints_loader.get_url(GET_CI_SCHEMA)

    def teardown_method(self):
        """
        This function deletes the test CI with survey_id:3456 at the end of each integration test to ensure it
        is not reflected in the firestore and schemas.
        """
        querystring = urlencode({"survey_id": 3456})
        make_iap_request("DELETE", f"{endpoints_loader.get_url(DELETE_CI)}?{querystring}")

    def test_update_validator_version(self, setup_payload):
        """
        Test the 'Put Validator Version' endpoint successfully updates the validator version for a CI and that the updated published_at timestamp is reflected in the database.
        - Post a CI using the 'Post CI' endpoint
        - Update the validator version using the 'Put Validator Version' endpoint with the CI guid and new validator version
        - Assert that the response status code is 200 OK
        - Get the CI metadata using the 'Get CI Metadata V1' endpoint with the same classifier type, classifier value, language and survey id as the posted CI
        - Assert that the response status code is 200 OK
        - Assert that the response body contains the updated validator version and a new published_at timestamp compared to the original published_at timestamp when the CI was created
        """
        # create post parameters
        data = create_post_params(1, validator_version="0.0.1")

        # Use `Post CI` to create ci metadata and schema in CIR
        ci_response = make_iap_request("POST", f"{self.post_url}?{data[0]}", json=setup_payload)

        # Assert response status code is 200 OK
        assert ci_response.status_code == status.HTTP_200_OK

        ci_response_data = ci_response.json()

        # Extract the CI guid from the post response data
        ci_guid = parse_qs(data[0])["guid"][0]
        # Extract the original published_at timestamp from the post response data
        original_published_at = ci_response_data["published_at"]
        # Define the updated validator version
        updated_validator_version = "0.0.2"

        query_params = UpdateValidatorVersionV1Params(
            guid=ci_guid,
            validator_version=updated_validator_version
        )

        new_payload = setup_payload.copy()
        new_payload["sections"] = ["Test new section"]

        # Send request to `Put Validator Version` endpoint to update the validator version and the CI Schema in CIR
        put_response = make_iap_request("PUT",
                                          f"{self.update_validator}?{urlencode(query_params.__dict__)}",
                                          json=new_payload)

        # Assert response status code is 200 OK
        assert put_response.status_code == status.HTTP_200_OK

        put_response_data = put_response.json()

        survey_id = new_payload["survey_id"]
        classifier_type = CiClassifierService.get_classifier_type(new_payload)
        classifier_value = CiClassifierService.get_classifier_value(new_payload, classifier_type)
        language = new_payload["language"]

        expected_ci_response = CiMetadata(
            ci_version=1,
            data_version=new_payload["data_version"],
            validator_version=updated_validator_version,
            classifier_type=classifier_type,
            classifier_value=classifier_value,
            guid=ci_guid,
            language=language,
            published_at=put_response_data["published_at"],
            survey_id=survey_id,
            title=new_payload["title"]
        )

        # Assert the response body matches the expected CI metadata with the updated validator version
        assert put_response.json() == expected_ci_response.model_dump()

        querystring = urlencode(
            {
                "classifier_type": classifier_type,
                "classifier_value": classifier_value,
                "language": language,
                "survey_id": survey_id,
            }
        )
        # sends request to http_query_ci endpoint for data
        check_ci_in_db = make_iap_request("GET", f"{self.get_metadata_url}?{querystring}")
        check_ci_in_db_data = check_ci_in_db.json()

        # Assert that the response body contains the updated validator version, and a new published_at timestamp compared to the original published_at timestamp when the CI was created
        assert original_published_at != check_ci_in_db_data[0]["published_at"]
        assert expected_ci_response.model_dump() == check_ci_in_db_data[0]

        get_schema_response = make_iap_request("GET", f"{self.get_schema_url}?guid={ci_guid}")
        assert get_schema_response.status_code == status.HTTP_200_OK

        get_schema_response_data = get_schema_response.json()

        # Assert that the response body contains the updated CI schema with the new section added in the payload
        assert get_schema_response_data == PostCiSchemaV1Data(**new_payload).model_dump()

    def test_update_validator_version_returns_404_if_ci_not_found(self, setup_payload):
        """
        Test the 'Put Validator Version' endpoint returns a 404 status code if no CI is found with the given guid.
        - Update the validator version using the 'Put Validator Version' endpoint with a non-existent CI guid and new validator version
        - Assert that the response status code is 404 Not Found
        """
        query_params = UpdateValidatorVersionV1Params(
            guid="non-existent-guid",
            validator_version="0.0.2"
        )

        put_response = make_iap_request("PUT", f"{self.update_validator}?{urlencode(query_params.__dict__)}",
                                        json=setup_payload)

        assert put_response.status_code == status.HTTP_404_NOT_FOUND
        assert put_response.json()["message"] == "No results found"

    def test_update_validator_version_returns_400_if_invalid_parameters(self):
        """
        Test the 'Put Validator Version' endpoint returns a 400 status code if invalid_parameters are sent in the request.
        - Update the validator version using the 'Put Validator Version' endpoint with an invalid querystring
        - Assert that the response status code is 400 Bad Request
        - Assert that the response body contains the expected error message indicating the bad request
        """
        # Create a bad querystring with missing required parameters
        querystring = urlencode({"my_bad": "querystring"})

        put_response = make_iap_request("PUT", f"{self.update_validator}?{querystring}")

        assert put_response.status_code == status.HTTP_400_BAD_REQUEST
        assert put_response.json()["message"] == "Validation has failed"

    def test_update_validator_version_returns_400_if_no_payload(self, setup_payload):
        """
        Test the 'Put Validator Version' endpoint returns a 400 status code if no payload is sent in the request.
        - Post a CI using the 'Post CI' endpoint to ensure there is a CI in the database to update the validator version for
        - Extract the CI guid from the post response data
        - Update the validator version using the 'Put Validator Version' endpoint with a valid querystring but no payload
        - Assert that the response status code is 400 Bad Request
        - Assert that the response body contains the expected error message indicating the bad request
        """
        # create post parameters
        data = create_post_params(1, validator_version="0.0.1")

        # Use `Post CI` to create ci metadata and schema in CIR
        ci_response = make_iap_request("POST", f"{self.post_url}?{data[0]}", json=setup_payload)

        # Assert response status code is 200 OK
        assert ci_response.status_code == status.HTTP_200_OK

        # Extract the CI guid from the post response data
        ci_guid = parse_qs(data[0])["guid"][0]

        query_params = UpdateValidatorVersionV1Params(
            guid=ci_guid,
            validator_version="0.0.2"
        )

        put_response = make_iap_request("PUT", f"{self.update_validator}?{urlencode(query_params.__dict__)}")

        assert put_response.status_code == status.HTTP_400_BAD_REQUEST
        assert put_response.json()["message"] == "Validation has failed"
