import unittest
from urllib.parse import urlencode

from app.events.subscriber import Subscriber
from tests.integration_tests.utils import make_iap_request


class TestHttpGetCiValidatorMetadataV1(unittest.TestCase):
    base_url = "/v1/ci_validator_metadata"
    post_url_v1 = "/v1/publish_collection_instrument"
    post_url_v2 = "/v2/publish_collection_instrument"
    subscriber = Subscriber()

    def teardown_method(self):
        """
        This function deletes the test CI with survey_id:3456 at the end of each integration test to ensure it
        is not reflected in the firestore and schemas.
        """
        # Need to pull and acknowledge messages in any test where post_ci_v1 is called so the subscription doesn't
        # get clogged
        self.subscriber.pull_messages_and_acknowledge()
        querystring = urlencode({"survey_id": 3456})
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

        assert response.status_code == 200
        assert len(response.json()) == 3
        for i, ci_validator_metadata in enumerate(response.json()):
            assert ci_validator_metadata == setup_payload
            assert ci_validator_metadata["validator_version"] == ["v0.0.2", "v0.0.1", ""][i]

    def test_return_404_if_no_ci_validator_metadata(self):
        """
        What am I testing:
        http_get_ci_validator_metadata_v1 should return 404 if no CI validator metadata is found.
        """
        response = make_iap_request("GET", f"{self.base_url}")

        assert response.status_code == 404
        assert response.json()["message"] == "No CI validator metadata found"
