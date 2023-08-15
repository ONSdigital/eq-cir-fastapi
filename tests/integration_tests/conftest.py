import pytest

from app.repositories.firestore import query_latest_ci_version
from tests.integration_tests.utils import delete_docs, post_ci_v1


@pytest.fixture
def setup_publish_ci_return_payload():
    """
    checks if document(survey_id="3456") exists (ci_exists is a positive number),
    and deletes if it does makes post request to API

    Returns:
        payload: test ci to be submitted to API
        response: post ci response object

    """
    ci_exists = query_latest_ci_version("3456", "business", "welsh")
    if ci_exists:
        delete_docs("3456")

    payload = {
        "survey_id": "3456",
        "language": "welsh",
        "form_type": "business",
        "title": "NotDune",
        "schema_version": "1",
        "data_version": "1",
    }
    post_ci_v1(payload)
    return payload


@pytest.fixture
def setup_payload():
    ci_exists = query_latest_ci_version("3456", "business", "welsh")
    if ci_exists:
        delete_docs("3456")

    payload = {
        "survey_id": "3456",
        "language": "welsh",
        "form_type": "business",
        "title": "NotDune",
        "schema_version": "1",
        "data_version": "1",
        "status": "DRAFT",
    }
    return payload
