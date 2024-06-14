from urllib.parse import urlencode

from fastapi import status

from app.events.subscriber import Subscriber
from tests.integration_tests.utils import make_iap_request


class TestGetCiMetadataV1:
    """Tests for the `http_get_ci_metadata_v1` endpoint"""

    base_url = "/v1/ci_metadata"
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

    def test_post_3_ci_with_same_metadata_query_ci_returns_3(self, setup_payload):
        """
        What am I testing:
        http_get_ci_metadata_v1 should return three ci_versions if the same ci is posted thrice.
        """
        # post 3 ci with the same data
        for _ in range(3):
            make_iap_request("POST", f"{self.post_url}", json=setup_payload)

        survey_id = setup_payload["survey_id"]
        classifier_type = setup_payload["classifier_type"]
        classifier_value = setup_payload["classifier_value"]
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

        assert len(query_ci_response_data) == 3
        assert query_ci_response_data[2]["ci_version"] == 1
        assert query_ci_response_data[1]["ci_version"] == 2
        assert query_ci_response_data[0]["ci_version"] == 3

    def test_post_ci_with_different_language_only_returns_1(self, setup_payload):
        """
        What am I testing:
        http_get_ci_metadata_v1 should return appropriate ci if language is different
        """
        # post 3 ci with the same data
        for _ in range(3):
            # Posts the ci using http_post_ci endpoint
            make_iap_request("POST", f"{self.post_url}", json=setup_payload)

        survey_id = setup_payload["survey_id"]
        classifier_type = setup_payload["classifier_type"]
        classifier_value = setup_payload["classifier_value"]
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

        setup_payload["language"] = "English"
        make_iap_request("POST", f"{self.post_url}", json=setup_payload)
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

        assert len(query_ci_response_data) == 3
        assert len(new_language_query_ci_response_data) == 1
        assert new_language_query_ci_response_data[0]["language"] == "English"

    def test_post_ci_with_same_metadata_query_ci_returns_with_new_keys_sds_schema_description(self, setup_payload):
        """
        What am I testing:
        http_get_ci_metadata_v1 should return ci with new keys sds_schema and description when queried.
        """
        # post 3 ci with the same data
        setup_payload["sds_schema"] = "xx-ytr-1234-856"
        # Posts the ci using http_post_ci endpoint
        make_iap_request("POST", f"{self.post_url}", json=setup_payload)
        survey_id = setup_payload["survey_id"]
        classifier_type = setup_payload["classifier_type"]
        classifier_value = setup_payload["classifier_value"]
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
        query_ci_response_json = query_ci_response.json()
        assert "description" in query_ci_response_json[0]
        assert query_ci_response_json[0]["sds_schema"] == "xx-ytr-1234-856"
        assert query_ci_response_json[0]["description"] == setup_payload["description"]

    def test_metadata_query_ci_returns_404(self, setup_payload):
        """
        What am I testing:
        http_get_ci metadata_v1 should return 404 status code if ci is not found.
        """
        survey_id = setup_payload["survey_id"]
        classifier_type = setup_payload["classifier_type"]
        classifier_value = setup_payload["classifier_value"]
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
        assert query_ci_response.status_code == status.HTTP_404_NOT_FOUND
        query_ci_response = query_ci_response.json()
        assert query_ci_response["message"] == "No results found"
        assert query_ci_response["status"] == "error"

    def test_metadata_query_ci_returns_400(self, setup_payload):
        """
        What am I testing:
        http_get_ci metadata_v1 should return 400 status code if incorrect args are provided.
        """
        survey_id = setup_payload["survey_id"]
        classifier_type = setup_payload["classifier_type"]
        classifier_value = None
        language = setup_payload["language"]
        querystring = urlencode(
            {
                "survey_id": survey_id,
                "classifier_type": classifier_type,
                "classifier_value": classifier_value,
                "language": language,
            }
        )

        response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_metadata_query_ci_returns_unauthorized_request(self, setup_payload):
        """
        What am I testing:
        http_get_ci metadata_v1 should return a 401 unauthorized error if the endpoint is requested with an unauthorized token.
        """
        survey_id = setup_payload["survey_id"]
        classifier_type = setup_payload["classifier_type"]
        classifier_value = setup_payload["classifier_value"]
        language = setup_payload["language"]
        querystring = urlencode(
            {
                "survey_id": survey_id,
                "classifier_type": classifier_type,
                "classifier_value": classifier_value,
                language: "language",
            }
        )
        response = make_iap_request("GET", f"{self.base_url}?{querystring}", unauthenticated=True)
        print(response)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
