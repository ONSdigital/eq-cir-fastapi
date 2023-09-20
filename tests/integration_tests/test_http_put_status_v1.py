from urllib.parse import urlencode

from fastapi import status

from app.events.subscriber import Subscriber
from tests.integration_tests.utils import (
    delete_docs,
    get_ci_metadata_v1,
    make_iap_request,
    post_ci_v1,
)


class TestPutStatusV1:
    base_url = "/v1/update_status"
    subscriber = Subscriber()

    def teardown_method(self):
        print(": tearing down")
        delete_docs("3456")

    def test_update_status(self, setup_payload):
        """
        Test AC-1: When I call the endpoint with a valid GUID where the status is Draft,
        the endpoint will update the status to Published and the endpoint returns
        the success payload {  "status":"success",
        "message": "CI status has already been changed to Published for <GUID>."  }
        """
        post_ci_v1(setup_payload)
        self.subscriber.pull_messages_and_acknowledge()

        survey_id = setup_payload["survey_id"]
        form_type = setup_payload["form_type"]
        language = setup_payload["language"]
        querystring = urlencode({"form_type": form_type, "language": language, "survey_id": survey_id})
        # sends request to http_query_ci endpoint for data
        query_ci_pre_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        query_ci_pre_response_data = query_ci_pre_response.json()

        ci_id = query_ci_pre_response_data[0]["id"]
        assert query_ci_pre_response_data[0]["status"] == "DRAFT"

        querystring = urlencode({"guid": ci_id})
        ci_update = make_iap_request("PUT", f"{self.base_url}?{querystring}")
        assert ci_update.status_code == status.HTTP_200_OK

        # returning text as opposed to json as its a string
        ci_update_data = ci_update.json()
        assert ci_update_data == f"CI status has been changed to Published for {ci_id}."

        # sends request to http_query_ci endpoint for data
        query_ci_post_response = make_iap_request("GET", f"{self.base_url}?{querystring}")
        query_ci_post_response_data = query_ci_post_response.json()

        assert query_ci_post_response_data[0]["id"] == ci_id
        assert query_ci_post_response_data[0]["status"] == "PUBLISHED"

        """
        Test AC-2: When I call the endpoint with a valid GUID where the status
        is already Published, the endpoint will return the correct status payload
        {  "status":"success", "message": "CI status has already
        been changed to Published for <GUID>."  }
        """

        querystring = urlencode({"guid": ci_id})
        ci_update = make_iap_request("PUT", f"{self.base_url}?{querystring}")
        assert ci_update.status_code == status.HTTP_200_OK

        # returning text as opposed to json as its a string
        ci_update_data = ci_update.json()
        assert ci_update_data == f"CI status has already been changed to Published for {ci_id}."

        # sends request to http_query_ci endpoint for data
        query_ci_post_response = get_ci_metadata_v1(survey_id, form_type, language)
        query_ci_post_response_data = query_ci_post_response.json()

        assert query_ci_post_response_data[0]["id"] == ci_id
        assert query_ci_post_response_data[0]["status"] == "PUBLISHED"

    def test_guid_not_found(self):
        """
        Test AC-3: When I call the endpoint with an invalid GUID, the endpoint will
        return the error payload { "status":"success", "message": "No CI found for <GUID>."}
        """
        ci_id = "404"
        querystring = urlencode({"guid": ci_id})
        ci_update = make_iap_request("PUT", f"{self.base_url}?{querystring}")
        assert ci_update.status_code == status.HTTP_404_NOT_FOUND

        ci_update_data = ci_update.json()
        assert ci_update_data == {
            "message": f"No CI metadata found for: {ci_id}",
            "status": "error",
        }
