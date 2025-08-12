from urllib.parse import urlencode

from app.config import settings
from app.models.responses import CiValidatorMetadata
from app.services.ci_classifier_service import CiClassifierService
from tests.integration_tests.utils import make_iap_request


class TestHttpGetCiValidatorMetadataV1:
    survey_id = "3456"
    base_url = "/v1/ci_validator_metadata"
    post_url_v1 = "/v1/publish_collection_instrument"
    post_url_v2 = "/v2/publish_collection_instrument"

    def teardown_method(self):
        """
        This function deletes the test CI with survey_id:3456 at the end of each integration test to ensure it
        is not reflected in the firestore and schemas.
        """
        querystring = urlencode({"survey_id": self.survey_id})
        make_iap_request("DELETE", f"/v1/dev/teardown?{querystring}")

    def test_retrieve_all_ci_validator_metadata(self, setup_payload):
        """
        What am I testing:
        http_get_ci_validator_metadata_v1 should return all CI validator metadata.
        """
        # Post CIs to create metadata
        # Post CI with v1 endpoint, validator version = empty
        make_iap_request("POST", f"{self.post_url_v1}", json=setup_payload)
        # Post CI with v2 endpoint, validator version = v0.0.1
        querystring = urlencode({"validator_version": "v0.0.1"})
        make_iap_request("POST", f"{self.post_url_v2}?{querystring}", json=setup_payload)
        # Post CI with v2 endpoint, validator version = v0.0.2
        querystring = urlencode({"validator_version": "v0.0.2"})
        make_iap_request("POST", f"{self.post_url_v2}?{querystring}", json=setup_payload)

        # Retrieve all CI validator metadata
        response = make_iap_request("GET", f"{self.base_url}")

        # Get classifier type and value for assertions
        classifier_type = CiClassifierService.get_classifier_type(setup_payload)
        classifier_value = CiClassifierService.get_classifier_value(setup_payload, classifier_type)

        # Assert the response status code and retrieve the metadata list
        assert response.status_code == 200
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
            assert ci_validator_metadata["validator_version"] == ["v0.0.2", "v0.0.1", ""][i]
            assert isinstance(CiValidatorMetadata(**ci_validator_metadata), CiValidatorMetadata)
