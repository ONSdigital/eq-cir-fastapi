import json
from urllib.parse import urlencode

import pytest
from fastapi import status

from app.config import settings
from tests.integration_tests.utils import make_iap_request, create_post_params
from tests.test_config.endpoints import ENDPOINTS, DELETE_CI, POST_CI, GET_CI_SCHEMA
from tests.test_config.endpoints_loader import EndpointsLoader

endpoints_loader = EndpointsLoader(ENDPOINTS, ignore_deprecated=True)


class TestDeleteCi:
    """
    Integration tests for the 'Delete CI' endpoint.
    """

    base_url = endpoints_loader.get_url(DELETE_CI)

    post_params = create_post_params(1)

    post_url = f"{endpoints_loader.get_url(POST_CI)}?{post_params[0]}"

    get_schema_url = endpoints_loader.get_url(GET_CI_SCHEMA)

    def test_can_delete_ci_returns_200(self, setup_payload):
        """
        When a survey_id is provided in the querystring parameters and a CI exists for that survey_id,
        the endpoint should delete the metadata and schema and return a 200 status code and a success message,
        and the deleted CI metadata should no longer be found when searched for by guid.
        """
        survey_id = setup_payload["survey_id"]
        querystring = urlencode({"survey_id": survey_id})

        # Create a CI to delete later and confirm it worked
        response = make_iap_request("POST", f"{self.post_url}", json=setup_payload)
        assert response.status_code == status.HTTP_200_OK

        guid = response.json()["guid"]

        # Send request to the Delete CI endpoint
        response = make_iap_request("DELETE", f"{self.base_url}?{querystring}")
        assert response.text == json.dumps(f"CI metadata and schema successfully deleted for {survey_id}.")
        assert response.status_code == status.HTTP_200_OK

        # Confirm CI metadata is deleted and cannot be found
        response = make_iap_request("GET", f"{self.get_schema_url}?guid={guid}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_can_delete_ci_returns_400(self):
        """
        When the required querystring parameter `survey_id` is not included in the request,
        the endpoint should return a 400 status code and an error message.
        """
        querystring = urlencode({"my_bad": "param"})
        # Send request to http_delete_ci endpoint
        response = make_iap_request("DELETE", f"{self.base_url}?{querystring}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["message"] == "Invalid search parameters provided"

    def test_can_delete_ci_returns_404_not_found(self):
        """
        When a CI does not exist for a provided survey_id, the endpoint should return a 404 status code and an error message.
        """
        survey_id = "non-existent-survey-id"
        querystring = urlencode({"survey_id": survey_id})
        # Send request to http_delete_ci endpoint
        response = make_iap_request("DELETE", f"{self.base_url}?{querystring}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["message"] == "No CI to delete"

    def test_delete_ci_returns_unauthorized_request(self, setup_payload):
        """
        When a request is sent to the endpoint without authentication, the endpoint should return a 401 status code and an error message.
        """
        if settings.CONF == "local-int-tests":
            pytest.skip("Skipping test_delete_ci_returns_unauthorized_request on local environment")

        survey_id = setup_payload["survey_id"]
        querystring = urlencode({"survey_id": survey_id})
        response = make_iap_request("DELETE", f"{self.base_url}?{querystring}", unauthenticated=True)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
