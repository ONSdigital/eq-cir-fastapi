from urllib.parse import urlencode

import pytest
from fastapi import status

from app.config import settings
from app.services.ci_classifier_service import CiClassifierService
from tests.integration_tests.utils import make_iap_request, create_post_params
from tests.test_config.endpoints import ENDPOINTS, GET_CI_METADATA, POST_CI, DELETE_CI
from tests.test_config.endpoints_loader import EndpointsLoader

endpoints_loader = EndpointsLoader(ENDPOINTS)


class TestGetCiMetadataV2:
    """
    Integration tests for the 'Get Ci Metadata V2' endpoint.
    """

    base_url = endpoints_loader.get_url(GET_CI_METADATA)

    param_list = create_post_params(3)
    post_url = endpoints_loader.get_url(POST_CI)

    def teardown_method(self):
        """
        This function deletes the test CI with survey_id:3456 at the end of each integration test to ensure it
        is not reflected in the firestore and schemas.
        """
        querystring = urlencode({"survey_id": 3456})
        make_iap_request("DELETE", f"{endpoints_loader.get_url(DELETE_CI)}?{querystring}")

    def test_post_3_ci_with_same_metadata_get_ci_metadata_v2_returns_3(self, setup_payload):
        """
        Test the 'Get Ci Metadata V2' endpoint returns all CIs that satisfies the parameters:
        - Post 3 identical CIs using the 'Post CI' endpoint with the same metadata (same survey_id, classifier_type, classifier_value and language)
        - Get CIs using the 'Get Ci Metadata V1' endpoint with the same parameters
        - Assert that the response status code is 200 OK
        - Assert that 3 CIs are returned and they are in the correct order based on ci_version (the latest ci should be returned first)
        """
        for data in self.param_list:
            make_iap_request("POST", f"{self.post_url}?{data}", json=setup_payload)

        classifier_type = CiClassifierService.get_classifier_type(setup_payload)
        classifier_value = CiClassifierService.get_classifier_value(setup_payload, classifier_type)

        get_ci_metadata_v2_payload = {
            "classifier_type": classifier_type,
            "classifier_value": classifier_value,
            "language": setup_payload["language"],
            "survey_id": setup_payload["survey_id"],
        }
        querystring = urlencode(get_ci_metadata_v2_payload)

        # sends request to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_response = make_iap_request("GET", f"{self.base_url}?{querystring}")

        assert get_ci_metadata_v2_response.status_code == status.HTTP_200_OK
        get_ci_metadata_v2_response_data = get_ci_metadata_v2_response.json()

        assert len(get_ci_metadata_v2_response_data) == 3
        assert get_ci_metadata_v2_response_data[2]["ci_version"] == 1
        assert get_ci_metadata_v2_response_data[1]["ci_version"] == 2
        assert get_ci_metadata_v2_response_data[0]["ci_version"] == 3

    def test_get_ci_metadata_v2_returns_all_metadata(self, setup_payload):
        """
        Test the 'Get Ci Metadata V2' endpoint returns all CIs that satisfies the parameters:
        - Post 3 identical CIs using the 'Post CI' endpoint with the same metadata (same survey_id, classifier_type, classifier_value and language)
        - Post another CI with the same metadata but different form_type
        - Get CIs using the 'Get Ci Metadata V2' endpoint without any query parameters to filter the results
        - Assert that the response status code is 200 OK
        - Assert that 4 CIs are returned since the query does not filter by form_type
        """
        # Post 3 different versions of the same CI
        for data in self.param_list:
            make_iap_request("POST", f"{self.post_url}?{data}", json=setup_payload)

        # Post a CI with different form_type
        new_payload = setup_payload.copy()
        new_payload["form_type"] = "something-else"
        params = {
            "validator_version": f"0.0.10",
            "guid": f"test-guid-10",
            "ci_version": 1,
        }
        make_iap_request("POST", f"{self.post_url}?{urlencode(params)}", json=new_payload)

        # Passing an empty list to the get_ci_metadata_v2
        get_ci_metadata_v2_response = make_iap_request("GET", f"{self.base_url}")
        get_ci_metadata_v2_response_data = get_ci_metadata_v2_response.json()

        # The response should include all 4 posted CIs since no query parameters were provided to filter the results
        assert get_ci_metadata_v2_response.status_code == status.HTTP_200_OK

        # Filter result with test survey id
        get_ci_metadata_v2_response_data = [ci for ci in get_ci_metadata_v2_response_data if ci["survey_id"] == setup_payload["survey_id"]]
        assert len(get_ci_metadata_v2_response_data) == 4

    def test_post_ci_with_different_language_only_returns_1(self, setup_payload):
        """
        Test the 'Get Ci Metadata V2' endpoint returns the CI with the correct language when multiple CIs with the same metadata but different language are posted:
        - Post a CI using the 'Post CI' endpoint with specific metadata and language
        - Post another CI using the 'Post CI' endpoint with the same metadata but different language
        - Get CIs using the 'Get Ci Metadata V2' endpoint with the metadata and the language of the first CI
        - Assert that the response status code is 200 OK
        - Assert that only 1 CI is returned and it is the one with the correct language
        """
        data = create_post_params(1)

        make_iap_request("POST", f"{self.post_url}?{data[0]}", json=setup_payload)

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
        query_ci_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        query_ci_response_data = query_ci_response.json()

        assert query_ci_response.status_code == status.HTTP_200_OK
        assert len(query_ci_response_data) == 1

        new_payload = setup_payload.copy()
        new_payload["language"] = "English"
        data = create_post_params(1)
        make_iap_request("POST", f"{self.post_url}?{data[0]}", json=new_payload)
        querystring = urlencode(
            {
                "classifier_type": classifier_type,
                "classifier_value": classifier_value,
                "language": "English",
                "survey_id": survey_id,
            }
        )
        # sends request to http_query_ci endpoint for data
        new_language_query_ci_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        new_language_query_ci_response_data = new_language_query_ci_response.json()

        assert new_language_query_ci_response.status_code == status.HTTP_200_OK
        assert len(new_language_query_ci_response_data) == 1
        assert new_language_query_ci_response_data[0]["language"] == "English"

    def test_post_ci_with_same_metadata_query_ci_returns_with_new_keys_sds_schema(self, setup_payload):
        """
        Test the 'Get Ci Metadata V2' endpoint returns the CI with the new key 'sds_schema' when a CI with the same metadata but with the 'sds_schema' key is posted:
        - Post a CI using the 'Post CI' endpoint with the same metadata but with the 'sds_schema' key
        - Get CIs using the 'Get Ci Metadata V2' endpoint with the same metadata
        - Assert that the response status code is 200 OK
        - Assert that the returned CI has the 'sds_schema' key and the value is correct
        """
        # post 3 ci with the same data
        new_payload = setup_payload.copy()
        new_payload["sds_schema"] = "xx-ytr-1234-856"
        # Posts the ci using http_post_ci endpoint

        data = create_post_params(1)

        make_iap_request("POST", f"{self.post_url}?{data[0]}", json=new_payload)

        classifier_type = CiClassifierService.get_classifier_type(setup_payload)
        classifier_value = CiClassifierService.get_classifier_value(setup_payload, classifier_type)

        get_ci_metadata_v2_payload = {
            "classifier_type": classifier_type,
            "classifier_value": classifier_value,
            "language": setup_payload["language"],
            "survey_id": setup_payload["survey_id"],
        }
        querystring = urlencode(get_ci_metadata_v2_payload)

        # sends request to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        query_ci_response_json = get_ci_metadata_v2_response.json()

        assert get_ci_metadata_v2_response.status_code == status.HTTP_200_OK
        assert len(query_ci_response_json) == 1
        assert query_ci_response_json[0]["sds_schema"] == "xx-ytr-1234-856"

    def test_metadata_query_v2_returns_404(self, setup_payload):
        """
        Test the 'Get Ci Metadata V2' endpoint returns 404 when no CI metadata is found for the given parameters:
        - Get CIs using the 'Get Ci Metadata V2' endpoint with parameters that do not match any existing CI metadata
        - Assert that the response status code is 404 Not Found
        - Assert that the response message indicates no results found
        """
        classifier_type = CiClassifierService.get_classifier_type(setup_payload)
        classifier_value = CiClassifierService.get_classifier_value(setup_payload, classifier_type)

        get_ci_metadata_v2_payload = {
            "classifier_type": classifier_type,
            "classifier_value": classifier_value,
            "language": setup_payload["language"],
            "survey_id": setup_payload["survey_id"],
        }
        querystring = urlencode(get_ci_metadata_v2_payload)

        # sends request to http_get_ci_metadata_v2 endpoint for data
        get_ci_metadata_v2_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        assert get_ci_metadata_v2_response.status_code == status.HTTP_404_NOT_FOUND
        query_ci_response = get_ci_metadata_v2_response.json()
        assert query_ci_response["message"] == "No CI found"
        assert query_ci_response["status"] == "error"

    def test_metadata_query_ci_returns_400(self, setup_payload):
        """
        Test the 'Get Ci Metadata V2' endpoint returns 400 when invalid query parameters are provided:
        - Get CIs using the 'Get Ci Metadata V2' endpoint with invalid query parameters
        - Assert that the response status code is 400 Bad Request
        - Assert that the response message indicates invalid search parameters
        """
        survey_id = setup_payload["survey_id"]
        classifier_type = CiClassifierService.get_classifier_type(setup_payload)
        classifier_value = CiClassifierService.get_classifier_value(setup_payload, classifier_type)
        language = setup_payload["language"]
        querystring = urlencode(
            {
                "survey_id": survey_id,
                "classifier_type": classifier_type,
                "incorrect_args": classifier_value,
                "language": language,
            }
        )

        response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert response_json["message"] == "Invalid search parameters provided"

    def test_metadata_query_ci_v2_returns_unauthorized_request(self, setup_payload):
        """
        Test the 'Get Ci Metadata V2' endpoint returns 401 when the request is not authenticated:
        - Get CIs using the 'Get Ci Metadata V2' endpoint with valid parameters but with invalid authentication
        - Assert that the response status code is 402 Unauthorized
        """
        if settings.CONF == "local-int-tests":
            pytest.skip("Skipping test_metadata_query_ci_v2_returns_unauthorized_request on local environment")

        classifier_type = CiClassifierService.get_classifier_type(setup_payload)
        classifier_value = CiClassifierService.get_classifier_value(setup_payload, classifier_type)

        get_ci_metadata_v2_payload = {
            "classifier_type": classifier_type,
            "classifier_value": classifier_value,
            "language": setup_payload["language"],
            "survey_id": setup_payload["survey_id"],
        }
        querystring = urlencode(get_ci_metadata_v2_payload)
        response = make_iap_request("GET", f"{self.base_url}?{querystring}", unauthenticated=True)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
