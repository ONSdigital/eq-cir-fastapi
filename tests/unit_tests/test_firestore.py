from app.config import logging
from app.repositories.firestore import (
    query_latest_ci_version,
    query_latest_ci_version_id,
)

logger = logging.getLogger(__name__)
logger.info("***test_true.py")

mock_survey_id = "123"
mock_form_type = "ft"
mock_language = "en-US"
mock_survey_1 = {
    "survey_id": mock_survey_id,
    "form_type": mock_form_type,
    "language": mock_language,
    "ci_version": 1,
    "status": "DRAFT",
}

mock_survey_2 = {
    "survey_id": mock_survey_id,
    "form_type": mock_form_type,
    "language": mock_language,
    "ci_version": 2,
    "status": "DRAFT",
}


def test_get_latest_ci_version_id_returns_latest_ci_version(mock_firestore_collection):
    mock_firestore_collection.document().set(mock_survey_1)
    mock_firestore_collection.document().set(mock_survey_2)
    ci_version = query_latest_ci_version(
        mock_survey_id,
        mock_form_type,
        mock_language,
    )
    assert ci_version == 2


def test_get_latest_ci_version_id_returns_0(mock_firestore_collection):
    ci_version = query_latest_ci_version(
        mock_survey_id,
        mock_form_type,
        mock_language,
    )
    assert ci_version == 0


def test_get_latest_ci_version_id_returns_latest_id(mock_firestore_collection):
    mock_firestore_collection.document("1").set(mock_survey_1)
    mock_firestore_collection.document("2").set(mock_survey_2)
    ci_id = query_latest_ci_version_id(mock_survey_id, mock_form_type, mock_language)
    assert ci_id == "2"


def test_get_latest_ci_version_id_returns_none(mock_firestore_collection):
    mock_firestore_collection.document("123").set(mock_survey_1)
    mock_firestore_collection.document("456").set(mock_survey_2)
    ci_id = query_latest_ci_version_id("124", mock_form_type, mock_language)
    assert not ci_id
