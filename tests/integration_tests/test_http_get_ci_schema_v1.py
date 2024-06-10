from dataclasses import asdict
from urllib.parse import urlencode

from fastapi import status

from app.events.subscriber import Subscriber
from app.models.requests import GetCiSchemaV1Params
from tests.integration_tests.utils import make_iap_request


class TestHttpGetCiSchemaV1:
    """Tests for the `http_get_ci_schema_v1` endpoint"""

    # Initialise the subscriber client
    subscriber = Subscriber()
    url = "/v1/retrieve_collection_instrument"
    post_url = "/v1/publish_collection_instrument"

    def teardown_method(self):
        """
        This function deletes the test CI with survey_id:3456 at the end of each integration test to ensure it
        is not reflected in the firestore and schemas.
        """
        # Need to pull and acknowledge messages in any test where post_ci_v1 is called so the subscription doesn't get clogged
        self.subscriber.pull_messages_and_acknowledge()
        querystring = urlencode({"survey_id": 3456})
        make_iap_request("DELETE", f"/v1/dev/teardown?{querystring}")

    def test_endpoint_returns_400_bad_request_if_bad_query(self):
        """
        What am I testing:
        `http_get_ci_schema_v1` should return `HTTP_400_BAD_REQUEST` status if a bad query is made
        via a GET request
        """
        # Create a bad querystring
        querystring = urlencode({"my_bad": "querystring"})
        # sends request to http_get_ci_schema_v1 endpoint for data
        response = make_iap_request("GET", f"{self.url}?{querystring}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_endpoint_returns_404_not_found_if_ci_not_found(self, setup_payload):
        """
        What am I testing:
        `http_get_ci_schema_v1` should return `HTTP_404_NOT_FOUND` status if a valid query is
        made via a GET request but a corresponding ci schema is not found on the db
        """
        # Construct a valid querystring using `setup_payload` data
        query_params = GetCiSchemaV1Params(
            classifier_type=setup_payload["form_type"],
            classifier_value=setup_payload["classifier_value"],
            language=setup_payload["language"],
            survey_id=setup_payload["survey_id"],
        )
        querystring = urlencode(asdict(query_params))

        # Endpoint should return `HTTP_404_NOT_FOUND` as no ci exist in the db
        response = make_iap_request("GET", f"{self.url}?{querystring}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_endpoint_returns_200_success_if_ci_schema_found(self, setup_payload):
        """
        What am I testing:
        `http_get_ci_schema_v1` should return `HTTP_200_OK` status if valid ci metadata and schema
        exist and a valid query to return the schema is made via a GET request
        """
        # Use `post_ci_v1` to create ci metadata and schema on the db
        make_iap_request("POST", f"{self.post_url}", json=setup_payload)

        # Construct the querystring to retrieve newly created ci schema
        query_params = GetCiSchemaV1Params(
            classifier_type=setup_payload["form_type"],
            classifier_value=setup_payload["classifier_value"],
            language=setup_payload["language"],
            survey_id=setup_payload["survey_id"],
        )
        querystring = urlencode(asdict(query_params))
        # sends request to http_get_ci_schema_v1 endpoint for data
        response = make_iap_request("GET", f"{self.url}?{querystring}")
        assert response.status_code == status.HTTP_200_OK

    def test_endpoint_returns_unauthorized_request(self, setup_payload):
        """
        What am I testing:
        http_get_ci_schema_v1 should return a 401 unauthorized error if the endpoint is requested with an unauthorized token.
        """
        query_params = GetCiSchemaV1Params(
            classifier_type=setup_payload["form_type"],
            classifier_value=setup_payload["classifier_value"],
            language=setup_payload["language"],
            survey_id=setup_payload["survey_id"],
        )

        querystring = urlencode(asdict(query_params))

        response = make_iap_request("GET", f"{self.url}?{querystring}", unauthenticated=True)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
