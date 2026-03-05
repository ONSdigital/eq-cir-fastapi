from app.repositories.firebase.ci_firebase_repository import CiFirebaseRepository
from tests.test_data.ci_test_data import (
    mock_ci_metadata,
    mock_classifier_type,
    mock_classifier_value,
    mock_id,
    mock_language,
    mock_next_version_ci_metadata,
    mock_next_version_id,
    mock_survey_id,
)


class TestCiFirebaseRepository:
    """
    Tests for the `CiFirebaseRepository` class.
    `ci_collection` is mocked out and replaced with `MockFirestore.collection` for all tests.
    """

    def test_query_ci_by_survey_id_returns_single_ci_if_found(self, mock_firestore_collection):
        """
        `get_ci_metadata_collection_with_survey_id` should return a list of a single ci
        if ci with input `survey_id` is found in the firestore db
        """
        firestore_client = CiFirebaseRepository()

        # Create a single ci in the db
        mock_firestore_collection.document().set(mock_ci_metadata.__dict__)

        found_ci = firestore_client.get_ci_metadata_collection_with_survey_id(mock_survey_id)

        assert found_ci == [mock_ci_metadata]

    def test_query_ci_by_survey_id_returns_multiple_ci_if_found(self, mock_firestore_collection):
        """
        `get_ci_metadata_collection_with_survey_id` should return a list of multiple ci
        if ci with input `survey_id` are found in the firestore db. Ci should be ordered in
        descending `ci_version` order
        """
        firestore_client = CiFirebaseRepository()

        # Create multiple ci in the db
        mock_firestore_collection.document().set(mock_next_version_ci_metadata.__dict__)
        mock_firestore_collection.document().set(mock_ci_metadata.__dict__)

        found_ci = firestore_client.get_ci_metadata_collection_with_survey_id(mock_survey_id)

        assert found_ci == [mock_next_version_ci_metadata, mock_ci_metadata]

    def test_query_ci_by_survey_id_returns_empty_list_if_ci_not_found(self, mock_firestore_collection):
        """
        `get_ci_metadata_collection_with_survey_id` should return an empty list if ci with input `survey_id`
        are not found in the firestore db
        """
        firestore_client = CiFirebaseRepository()

        found_ci = firestore_client.get_ci_metadata_collection_with_survey_id(mock_survey_id)

        assert found_ci == []

    def test_query_latest_ci_version_returns_latest_ci_version(self, mock_firestore_collection):
        """
        `get_latest_ci_metadata` should return the latest ci version for a given survey_id, classifier_type,
        classifier_value, and language
        """
        firestore_client = CiFirebaseRepository()

        # Create multiple ci in the db
        mock_firestore_collection.document().set(mock_ci_metadata.__dict__)
        mock_firestore_collection.document().set(mock_next_version_ci_metadata.__dict__)

        latest_ci_metadata = firestore_client.get_latest_ci_metadata(
            mock_survey_id,
            mock_classifier_type,
            mock_classifier_value,
            mock_language,
        )

        assert latest_ci_metadata.ci_version == 2

    def test_query_latest_ci_version_returns_0(self, mock_firestore_collection):
        """
        `get_latest_ci_metadata` should return None if no ci metadata is found for a given
        survey_id, classifier_type, classifier_value, and language
        """
        firestore_client = CiFirebaseRepository()

        latest_ci_metadata = firestore_client.get_latest_ci_metadata(
            mock_survey_id,
            mock_classifier_type,
            mock_classifier_value,
            mock_language,
        )

        assert latest_ci_metadata is None

    def test_query_latest_ci_version_id_returns_latest_id(self, mock_firestore_collection):
        """
        `get_latest_ci_metadata` should return the latest ci metadata for a given survey_id, form_type, and language
        """
        firestore_client = CiFirebaseRepository()

        # Create multiple ci in the db
        mock_firestore_collection.document(mock_id).set(mock_ci_metadata.__dict__)
        mock_firestore_collection.document(mock_next_version_id).set(mock_next_version_ci_metadata.__dict__)

        latest_ci_metadata = firestore_client.get_latest_ci_metadata(
            mock_survey_id, mock_classifier_type, mock_classifier_value, mock_language
        )

        assert latest_ci_metadata.guid == mock_next_version_id

    def test_query_latest_ci_version_id_returns_none(self, mock_firestore_collection):
        """
        `get_latest_ci_metadata` should return None if no ci metadata is found for a given query parameters
        """
        firestore_client = CiFirebaseRepository()

        # Create multiple ci in the db
        mock_firestore_collection.document().set(mock_ci_metadata.__dict__)
        mock_firestore_collection.document().set(mock_next_version_ci_metadata.__dict__)

        latest_ci_metadata = firestore_client.get_latest_ci_metadata(
            "wrong_survey_id", mock_classifier_type, mock_classifier_value, mock_language
        )

        assert latest_ci_metadata is None

    def test_get_query_ci_metadata_with_guid_returns_ci(self, mock_firestore_collection):
        """
        `get_ci_metadata_with_id` should return the ci metadata with the input `guid`
        """
        firestore_client = CiFirebaseRepository()

        # Create multiple ci in the db
        mock_firestore_collection.document(mock_id).set(mock_ci_metadata.__dict__)
        mock_firestore_collection.document(mock_next_version_id).set(mock_next_version_ci_metadata.__dict__)

        ci_metadata = firestore_client.get_ci_metadata_with_id(mock_id)

        assert ci_metadata == mock_ci_metadata

    def test_get_query_ci_metadata_with_guid_returns_none(self, mock_firestore_collection):
        """
        `get_ci_metadata_with_id` should return None if no ci metadata is found with the input `guid`
        """
        firestore_client = CiFirebaseRepository()

        # Create a single ci in the db
        mock_firestore_collection.document(mock_id).set(mock_ci_metadata.__dict__)

        ci_metadata = firestore_client.get_ci_metadata_with_id("wrong_guid")

        assert ci_metadata is None
