from unittest.mock import patch

from app.main import app

from fastapi.testclient import TestClient

from tests.test_data.ci_test_data import (
    mock_post_ci_schema,
    mock_post_ci_schema_without_sds_schema,
    mock_post_ci_schema_with_sds_schema,
    mock_survey_id,
    mock_form_type,
    mock_language,
)

client = TestClient(app)


class TestPostCiMetadata:
    """Tests for the `post_ci_metadata` firestore method"""

    url = "/v1/publish_collection_instrument"

    @patch("app.events.publisher.Publisher.publish_message")
    @patch("app.repositories.buckets.ci_schema_bucket_repository.CiSchemaBucketRepository.store_ci_schema")
    @patch("app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.get_latest_ci_metadata")
    def test_creates_new_ci_metadata_on_firestore(
        self, 
        mocked_get_latest_ci_metadata, 
        mocked_store_ci_schema,
        mocked_publish_message,
        mock_firestore_collection
        ):
        """
        `post_ci_metadata` should create a new ci metadata record on firestore if provided with valid data
        """
        # Mocked `get_latest_ci_metadata` should return None for this test, indicating no previous version of metadata is found
        mocked_get_latest_ci_metadata.return_value = None
        # Call the post ci endpoint
        client.post(self.url, headers={"ContentType": "application/json"}, json=mock_post_ci_schema.model_dump())

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


    @patch("app.events.publisher.Publisher.publish_message")
    @patch("app.repositories.buckets.ci_schema_bucket_repository.CiSchemaBucketRepository.store_ci_schema")    
    @patch("app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.get_latest_ci_metadata")
    def test_creates_new_ci_metadata_omits_optional_sds_schema_if_not_present(
        self, 
        mocked_get_latest_ci_metadata, 
        mocked_store_ci_schema,
        mocked_publish_message,
        mock_firestore_collection
        ):
        """
        `post_ci_metadata` should create a new ci metadata record on firestore if provided with
        valid data. If optional `sds_schema` is not proveded as part of the post data, this field
        should not be saved as part of the metadata on firestore
        """
        # Mocked `get_latest_ci_metadata` should return None for this test, indicating no previous version of metadata is found
        mocked_get_latest_ci_metadata.return_value = None
        # Call the post ci endpoint
        client.post(self.url, headers={"ContentType": "application/json"}, json=mock_post_ci_schema_without_sds_schema.model_dump())

        # Query the mocked firestore db and confirm the new record is there
        ci_metadata_query = (
            mock_firestore_collection.where("survey_id", "==", mock_survey_id)
            .where("form_type", "==", mock_form_type)
            .where("language", "==", mock_language)
            .limit(1)
            .stream()
        )
        # Confirm the ci returned as part of the query doesn't contain the `sds_schema` field
        for ci in ci_metadata_query:
            # ci should contain doc
            # `sds_schema` should not be present in created document keys
            assert "sds_schema" not in ci._doc.keys()

    @patch("app.events.publisher.Publisher.publish_message")
    @patch("app.repositories.buckets.ci_schema_bucket_repository.CiSchemaBucketRepository.store_ci_schema")
    @patch("app.repositories.firebase.ci_firebase_repository.CiFirebaseRepository.get_latest_ci_metadata")
    def test_creates_new_ci_metadata_includes_optional_sds_schema_if_present(
        self, 
        mocked_get_latest_ci_metadata, 
        mocked_store_ci_schema,
        mocked_publish_message,
        mock_firestore_collection
        ):
        """
        `post_ci_metadata` should create a new ci metadata record on firestore if provided with
        valid data. If optional `sds_schema` is proveded as part of the post data, this field
        should be saved as part of the metadata on firestore
        """
        # Mocked `get_latest_ci_metadata` should return None for this test, indicating no previous version of metadata is found
        mocked_get_latest_ci_metadata.return_value = None

        # Call the post ci endpoint
        client.post(self.url, headers={"ContentType": "application/json"}, json=mock_post_ci_schema_with_sds_schema.model_dump())
        # Query the mocked firestore db and confirm the new record is there
        ci_metadata_query = (
            mock_firestore_collection.where("survey_id", "==", mock_survey_id)
            .where("form_type", "==", mock_form_type)
            .where("language", "==", mock_language)
            .limit(1)
            .stream()
        )
        # Confirm the ci returned as part of the query contains the `sds_schema` field
        for ci in ci_metadata_query:
            # ci should contain doc and `sds_schema` should be present in created document keys
            assert "sds_schema" in ci._doc.keys()
            assert ci._doc["sds_schema"] == mock_post_ci_schema_with_sds_schema.sds_schema

    