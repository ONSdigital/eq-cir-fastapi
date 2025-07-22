from urllib.parse import urlencode

from app.models.requests import PatchValidatorVersionV1Params
from tests.integration_tests.utils import make_iap_request


class TestPatchValidatorVersionV1:

    post_url = "/v2/publish_collection_instrument?validator_version=0.0.1"
    update_validator = "/v1/update_validator_version/"

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
        ci_guid = ci_response_data["guid"]
        updated_validator_version = "0.0.2"

        query_params = PatchValidatorVersionV1Params(
            guid=ci_guid,
            validator_version=updated_validator_version

        )
        ci_update_response = make_iap_request("PATCH", f"{self.update_validator}?{urlencode(query_params.__dict__)}")
        ci_update_data = ci_update_response.json()

        assert ci_update_data["validator_version"] == updated_validator_version