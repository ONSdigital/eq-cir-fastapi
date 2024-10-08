from urllib.parse import urlencode

from fastapi import status

from app.events.subscriber import Subscriber
from app.services.ci_classifier_service import CiClassifierService
from tests.integration_tests.utils import make_iap_request


class TestGetCiMetadataV2:
    """Tests for the `http_get_ci_metadata_v2` endpoint."""

    base_url = "/v2/ci_metadata"
    post_url = "/v1/publish_collection_instrument"
    subscriber = Subscriber()

    def teardown_method(self):
        """
        This function deletes the test CI with survey_id:3456 at the end of each integration test to ensure it
        is not reflected in the firestore and schemas.
        """
        # Need to pull and acknowledge messages in any test where post_ci_v1 is called so the subscription doesn't get clogged
        self.subscriber.pull_messages_and_acknowledge()

        querystring = urlencode({"survey_id": 3456})
        make_iap_request("DELETE", f"/v1/dev/teardown?{querystring}")

    def test_post_3_ci_with_same_metadata_get_ci_metadata_v2_returns_3(self, setup_payload):
        """
        What am I testing:
        http_get_ci_metadata_v2 should return three ci_versions if the same ci is posted thrice.
        """
        for _ in range(3):
            # Posts the ci using http_post_ci endpoint
            make_iap_request("POST", f"{self.post_url}", json=setup_payload)

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
        get_ci_metadata_v2_response_data = get_ci_metadata_v2_response.json()

        assert len(get_ci_metadata_v2_response_data) == 3
        assert get_ci_metadata_v2_response_data[2]["ci_version"] == 1
        assert get_ci_metadata_v2_response_data[1]["ci_version"] == 2
        assert get_ci_metadata_v2_response_data[0]["ci_version"] == 3

    def test_get_ci_metadata_v2_returns_all_metadata(self):
        """
        What am I testing:
        http_get_ci_metadata_v2 should return all metadata if no args are provided for the query.
        """
        # Passing an empty list to the get_ci_metadata_v2
        get_ci_metadata_v2_response = make_iap_request("GET", f"{self.base_url}")
        get_ci_metadata_v2_response_data = get_ci_metadata_v2_response.json()
        assert len(get_ci_metadata_v2_response_data) > 0

    def test_post_ci_with_same_metadata_query_ci_returns_with_new_keys_sds_schema_description(self, setup_payload):
        """
        What am I testing:
        http_get_ci_metadata_v2 should return ci with new keys sds_schema and description when queried.
        """
        # post 3 ci with the same data
        setup_payload["sds_schema"] = "xx-ytr-1234-856"
        # Posts the ci using http_post_ci endpoint
        make_iap_request("POST", f"{self.post_url}", json=setup_payload)

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
        assert query_ci_response_json[0]["sds_schema"] == "xx-ytr-1234-856"
        assert query_ci_response_json[0]["description"] == setup_payload["description"]

    def test_metadata_query_v2_returns_404(self, setup_payload):
        """
        What am I testing:
        http_get_ci metadata_v2 should return 404 status code if ci is not found.
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

    def test_metadata_query_ci_v2_returns_unauthorized_request(self, setup_payload):
        """
        What am I testing:
        http_get_ci metadata_v2 should return a 401 unauthorized error if the endpoint is requested with an unauthorized token.
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
        response = make_iap_request("GET", f"{self.base_url}?{querystring}", unauthenticated=True)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
