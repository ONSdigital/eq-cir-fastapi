from urllib.parse import urlencode
from fastapi import status

from app.models.responses import CiValidatorMetadata
from app.services.ci_classifier_service import CiClassifierService
from tests.integration_tests.utils import make_iap_request, create_post_params
from tests.test_config.endpoints import ENDPOINTS, GET_CI_VALIDATOR_METADATA, POST_CI, DELETE_CI
from tests.test_config.endpoints_loader import EndpointsLoader

endpoints_loader = EndpointsLoader(ENDPOINTS)


class TestHttpGetCiValidatorMetadata:
    survey_id = "3456"
    base_url = endpoints_loader.get_url(GET_CI_VALIDATOR_METADATA)
    post_url = endpoints_loader.get_url(POST_CI)

    def teardown_method(self):
        """
        This function deletes the test CI with survey_id:3456 at the end of each integration test to ensure it
        is not reflected in the firestore and schemas.
        """
        querystring = urlencode({"survey_id": self.survey_id})
        make_iap_request("DELETE", f"{endpoints_loader.get_url(DELETE_CI)}?{querystring}")

    def test_retrieve_all_ci_validator_metadata(self, setup_payload):
        """
        What am I testing:
        get_collection_instruments_validator_metadata_v1 should return all CI validator metadata.
        """
        # Post CIs to create metadata
        # Post CI with v1 endpoint, validator version = empty
        data = create_post_params(1)
        make_iap_request("POST", f"{self.post_url}?{data[0]}", json=setup_payload)        # Post CI with v2 endpoint, validator version = v0.0.1
        data = create_post_params(1, "0.0.2")
        make_iap_request("POST", f"{self.post_url}?{data[0]}", json=setup_payload)        # Post CI with v2 endpoint, validator version = v0.0.2
        data = create_post_params(1, "0.0.3")
        make_iap_request("POST", f"{self.post_url}?{data[0]}", json=setup_payload)
        # Retrieve all CI validator metadata
        response = make_iap_request("GET", f"{self.base_url}")

        # Get classifier type and value for assertions
        classifier_type = CiClassifierService.get_classifier_type(setup_payload)
        classifier_value = CiClassifierService.get_classifier_value(setup_payload, classifier_type)

        # Assert the response status code and retrieve the metadata list
        assert response.status_code == status.HTTP_200_OK
        ci_validator_metadata_list = response.json()

        # filter list so that assertion only carry out on the expected metadata
        filtered_ci_validator_metadata_list = [
            metadata for metadata in ci_validator_metadata_list if metadata["survey_id"] == self.survey_id
        ]

        # Assert the length and content of the filtered metadata list
        assert len(filtered_ci_validator_metadata_list) == 3
        for i, ci_validator_metadata in enumerate(filtered_ci_validator_metadata_list):
            assert ci_validator_metadata["survey_id"] == setup_payload["survey_id"]
            assert ci_validator_metadata["classifier_type"] == classifier_type
            assert ci_validator_metadata["classifier_value"] == classifier_value
            assert ci_validator_metadata["ci_version"] == [3, 2, 1][i]
            assert ci_validator_metadata["validator_version"] == ["0.0.3", "0.0.2", "0.0.1"][i]
            assert isinstance(CiValidatorMetadata(**ci_validator_metadata), CiValidatorMetadata)

    def test_retrieve_no_ci_validator_metadata(self, setup_payload):
        """
        What am I testing:
        endpoint should return 404 if no CI validator metadata is found.
        """
        # Retrieve all CI validator metadata without posting any CI
        response = make_iap_request("GET", f"{self.base_url}")

        # Assert the response status code and content
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["message"] == "No CI validator metadata found"