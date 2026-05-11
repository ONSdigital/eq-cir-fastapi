from dataclasses import asdict
from urllib.parse import urlencode

import pytest
from fastapi import status

from app.config import settings
from app.models.requests import GetCiSchemaV1Params, PostCiSchemaV1Data
from app.services.ci_classifier_service import CiClassifierService
from tests.integration_tests.utils import make_iap_request, create_post_params
from tests.test_config.endpoints import ENDPOINTS, GET_CI_SCHEMA, POST_CI, DELETE_CI
from tests.test_config.endpoints_loader import EndpointsLoader

endpoints_loader = EndpointsLoader(ENDPOINTS)


class TestHttpGetCiSchemaV1:
    """
    Integration tests for the 'Get Ci Schema V1' endpoint.
    """

    url = endpoints_loader.get_url(GET_CI_SCHEMA)
    post_url = endpoints_loader.get_url(POST_CI)

    def teardown_method(self):
        """
        This function deletes the test CI with survey_id:3456 at the end of each integration test to ensure it
        is not reflected in the firestore and schemas.
        """
        querystring = urlencode({"survey_id": 3456})
        make_iap_request("DELETE", f"{endpoints_loader.get_url(DELETE_CI)}?{querystring}")

    def test_endpoint_returns_200_success_if_ci_schema_found(self, setup_payload):
        """
        Test the 'Get Ci Schema V1' endpoint returns a 200 success status if a ci schema is found with the given query parameters.
        - Post a CI using the 'Post CI' endpoint
        - Get the CI schema using the 'Get Ci Schema V1' endpoint with the same classifier type, classifier value, language and survey id as the posted CI
        - Assert that the response status code is 200 OK
        - Assert that the response body is the expected ci schema data corresponding to the posted CI
        """
        # Use `Post CI` to create ci metadata and schema on the db
        data = create_post_params(1)

        post_response = make_iap_request("POST", f"{self.post_url}?{data[0]}", json=setup_payload)

        assert post_response.status_code == status.HTTP_200_OK

        classifier_type = CiClassifierService.get_classifier_type(setup_payload)
        classifier_value = CiClassifierService.get_classifier_value(setup_payload, classifier_type)

        # Construct the querystring to retrieve newly created ci schema
        query_params = GetCiSchemaV1Params(
            classifier_type=classifier_type,
            classifier_value=classifier_value,
            language=setup_payload["language"],
            survey_id=setup_payload["survey_id"],
        )
        querystring = urlencode(asdict(query_params))

        # sends request to http_get_ci_schema_v1 endpoint for data
        response = make_iap_request("GET", f"{self.url}?{querystring}")
        assert response.status_code == status.HTTP_200_OK
        response_schema = response.json()

        # Assert that the response body is the expected ci schema
        assert response_schema == PostCiSchemaV1Data(**setup_payload).model_dump()

    def test_endpoint_returns_200_success_with_latest_schema_if_multiple_ci_schema_found(self, setup_payload):
        """
        Test the 'Get Ci Schema V1' endpoint returns a 200 success status if a ci schema is found with the given query parameters.
        - Post a CI using the 'Post CI' endpoint
        - Get the CI schema using the 'Get Ci Schema V1' endpoint with the same classifier type, classifier value, language and survey id as the posted CI
        - Assert that the response status code is 200 OK
        - Assert that the response body is the latest ci schema data of the posted CIs
        """
        num_of_schemas = 2
        # Use `Post CI` to create ci metadata and schema on the db
        data = create_post_params(num_of_schemas)

        payloads = [setup_payload.copy(), setup_payload.copy()]

        for i, payload in enumerate(payloads):
            payload["title"] = f"Test Schema version {i+1}"
            post_response = make_iap_request("POST", f"{self.post_url}?{data[i]}", json=payload)

            assert post_response.status_code == status.HTTP_200_OK

        classifier_type = CiClassifierService.get_classifier_type(setup_payload)
        classifier_value = CiClassifierService.get_classifier_value(setup_payload, classifier_type)

        # Construct the querystring to retrieve newly created ci schema
        query_params = GetCiSchemaV1Params(
            classifier_type=classifier_type,
            classifier_value=classifier_value,
            language=setup_payload["language"],
            survey_id=setup_payload["survey_id"],
        )
        querystring = urlencode(asdict(query_params))

        # sends request to http_get_ci_schema_v1 endpoint for data
        response = make_iap_request("GET", f"{self.url}?{querystring}")
        assert response.status_code == status.HTTP_200_OK
        response_schema = response.json()

        # Assert that the response body is the expected ci schema - the latest schema
        assert response_schema == PostCiSchemaV1Data(**payloads[-1]).model_dump()

    def test_endpoint_returns_400_bad_request_if_bad_query(self):
        """
        Test the 'Get Ci Schema V1' endpoint returns a 400 bad request status if a bad query is made to the endpoint.
         - Get the CI schema using the 'Get Ci Schema V1' endpoint with an invalid querystring
         - Assert that the response status code is 400 Bad Request
         - Assert that the response body contains the expected error message indicating the bad request
        """
        # Create a bad querystring
        querystring = urlencode({"my_bad": "querystring"})
        # sends request to http_get_ci_schema_v1 endpoint for data
        response = make_iap_request("GET", f"{self.url}?{querystring}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["message"] == "Invalid search parameters provided"

    def test_endpoint_returns_404_not_found_if_ci_not_found(self, setup_payload):
        """
        Test the 'Get Ci Schema V1' endpoint returns a 404 not found status if a ci schema is not found with the given query parameters.
         - Get the CI schema using the 'Get Ci Schema V1' endpoint with a valid querystring that does not match any ci schema in the database
         - Assert that the response status code is 404 Not Found
         - Assert that the response body contains the expected error message indicating that the ci schema was not found
        """
        classifier_type = CiClassifierService.get_classifier_type(setup_payload)
        classifier_value = CiClassifierService.get_classifier_value(setup_payload, classifier_type)

        # Construct a valid querystring using `setup_payload` data
        query_params = GetCiSchemaV1Params(
            classifier_type=classifier_type,
            classifier_value=classifier_value,
            language=setup_payload["language"],
            survey_id=setup_payload["survey_id"],
        )
        querystring = urlencode(asdict(query_params))

        # Endpoint should return `HTTP_404_NOT_FOUND` as no ci exist in the db
        response = make_iap_request("GET", f"{self.url}?{querystring}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["message"] == "No CI found"

    def test_endpoint_returns_unauthorized_request(self, setup_payload):
        """
        Test the 'Get Ci Schema V1' endpoint returns 401 when the request is not authenticated:
        - Make a request to the 'Get Ci Schema V1' endpoint with invalid authentication
        - Assert that the response status code is 401 Unauthorized
        """
        if settings.CONF == "local-int-tests":
            pytest.skip("Skipping test_endpoint_returns_unauthorized_request on local environment")

        classifier_type = CiClassifierService.get_classifier_type(setup_payload)
        classifier_value = CiClassifierService.get_classifier_value(setup_payload, classifier_type)

        query_params = GetCiSchemaV1Params(
            classifier_type=classifier_type,
            classifier_value=classifier_value,
            language=setup_payload["language"],
            survey_id=setup_payload["survey_id"],
        )

        querystring = urlencode(asdict(query_params))

        response = make_iap_request("GET", f"{self.url}?{querystring}", unauthenticated=True)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
