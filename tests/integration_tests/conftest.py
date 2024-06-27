from urllib.parse import urlencode

import pytest

from app.repositories.firebase.ci_firebase_repository import CiFirebaseRepository
from tests.integration_tests.utils import make_iap_request

firestore_client = CiFirebaseRepository()


@pytest.fixture
def setup_publish_ci_return_payload():
    """
    checks if document(survey_id="3456") exists (ci_exists is a positive number),
    and deletes if it does makes post request to API

    Returns:
        payload: test ci to be submitted to API
        response: post ci response object

    """
    ci_exists = firestore_client.get_latest_ci_metadata("3456", "form_type", "business", "welsh")
    if ci_exists:
        querystring = urlencode({"survey_id": 3456})
        make_iap_request("DELETE", f"/v1/dev/teardown?{querystring}")

    payload = {
        "survey_id": "3456",
        "language": "welsh",
        "classifier_type": "form_type",
        "classifier_value": "business",
        "title": "NotDune",
        "schema_version": "1",
        "data_version": "1",
        "description": "Version of CI is for March 2023",
    }
    make_iap_request("POST", "/v1/publish_collection_instrument", json=payload)
    return payload


@pytest.fixture
def setup_payload():
    ci_exists = firestore_client.get_latest_ci_metadata("3456", "form_type", "business", "welsh")
    if ci_exists:
        querystring = urlencode({"survey_id": 3456})
        make_iap_request("DELETE", f"/v1/dev/teardown?{querystring}")
    payload = {
        "survey_id": "3456",
        "language": "welsh",
        "classifier_type": "form_type",
        "classifier_value": "business",
        "title": "NotDune",
        "schema_version": "1",
        "data_version": "1",
        "description": "Version of CI is for March 2023",
    }
    return payload
