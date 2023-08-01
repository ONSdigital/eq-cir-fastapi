from unittest.mock import patch

from app.models.requests import PostCiMetadataV1PostData
from app.repositories.firestore import (
    query_ci_by_survey_id,
    query_latest_ci_version,
    query_latest_ci_version_id,
    post_ci_metadata,
)

# Mock data for all tests
mock_data_version = "1"
mock_form_type = "ft"
mock_language = "en-US"
mock_schema_version = "1"
mock_survey_id = "123"
mock_title = "My test survey"

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


class TestQueryCiBySurveyId:
    """Tests for the `query_ci_by_survey_id` firestore method"""

    def test_method_returns_single_ci_if_found(self, mock_firestore_collection):
        """
        `query_ci_by_survey_id` should return a list of a single ci if ci with input `survey_id` is
        found in the firestore db
        """
        # Create a single ci in the db
        mock_firestore_collection.document().set(mock_survey_1)
        found_ci = query_ci_by_survey_id(mock_survey_id)

        assert found_ci == [mock_survey_1]

    def test_method_returns_multiple_ci_if_found(self, mock_firestore_collection):
        """
        `query_ci_by_survey_id` should return a list of multiple ci if ci with input `survey_id`
        are found in the firestore db. Ci should be ordered in descending `ci_version` order
        """
        # Create multiple ci in the db
        mock_firestore_collection.document().set(mock_survey_1)
        mock_firestore_collection.document().set(mock_survey_2)
        found_ci = query_ci_by_survey_id(mock_survey_id)

        assert found_ci == [mock_survey_2, mock_survey_1]

    def test_method_returns_empty_list_if_ci_not_found(self, mock_firestore_collection):
        """
        `query_ci_by_survey_id` should return an empty list if ci with input `survey_id`
        are not found in the firestore db
        """
        found_ci = query_ci_by_survey_id(mock_survey_id)

        assert found_ci == []


class TestQueryLatestCiVersion:
    """Tests for the `query_latest_ci_version` firestore method"""

    def test_get_latest_ci_version_id_returns_latest_ci_version(self, mock_firestore_collection):
        mock_firestore_collection.document().set(mock_survey_1)
        mock_firestore_collection.document().set(mock_survey_2)
        ci_version = query_latest_ci_version(
            mock_survey_id,
            mock_form_type,
            mock_language,
        )
        assert ci_version == 2

    def test_get_latest_ci_version_id_returns_0(self, mock_firestore_collection):
        ci_version = query_latest_ci_version(
            mock_survey_id,
            mock_form_type,
            mock_language,
        )
        assert ci_version == 0


class TestQueryLatestCiVersionId:
    """Tests for the `query_latest_ci_version_id` firestore method"""

    def test_get_latest_ci_version_id_returns_latest_id(self, mock_firestore_collection):
        mock_firestore_collection.document("1").set(mock_survey_1)
        mock_firestore_collection.document("2").set(mock_survey_2)
        ci_id = query_latest_ci_version_id(mock_survey_id, mock_form_type, mock_language)
        assert ci_id == "2"

    def test_get_latest_ci_version_id_returns_none(self, mock_firestore_collection):
        mock_firestore_collection.document("123").set(mock_survey_1)
        mock_firestore_collection.document("456").set(mock_survey_2)
        ci_id = query_latest_ci_version_id("124", mock_form_type, mock_language)
        assert not ci_id


class TestPostCiMetadata:
    """Tests for the `post_ci_metadata` firestore method"""

    post_data = PostCiMetadataV1PostData(
        data_version=mock_data_version,
        form_type=mock_form_type,
        language=mock_language,
        title=mock_title,
        schema_version=mock_schema_version,
        survey_id=mock_survey_id,
    )

    @patch("app.repositories.firestore.query_latest_ci_version")
    def test_creates_new_ci_metadata_on_firestore(self, mocked_query_latest_ci_version, mock_firestore_collection):
        """
        `post_ci_metadata` should create a new ci metadata record on firestore if provided with valid data
        """
        # Mocked `query_latest_ci_version` should return 0 for this test
        mocked_query_latest_ci_version.return_value = 0
        # Call the function
        post_ci_metadata(self.post_data)
        # Query the mocked firestore db and confirm the new record is there
        ci_metadata_query = (
            mock_firestore_collection.where("survey_id", "==", mock_survey_id)
            .where("form_type", "==", mock_form_type)
            .where("language", "==", mock_language)
            .limit(1)
            .stream()
        )
        # Confirm the where query returns a valid object
        assert ci_metadata_query.__next__ is not None
