import datetime
import uuid

from app.config import Settings
from app.models.responses import CiMetadata, CiStatus

settings = Settings()


# Mock data for all tests
mock_ci_version = "1"
mock_data_version = "1"
mock_form_type = "ft"
mock_id = str(uuid.uuid4())
mock_language = "en-US"
mock_published_at = datetime.datetime.utcnow().strftime(settings.PUBLISHED_AT_FORMAT)
mock_schema_version = "1"
mock_sds_schema = "my test schema"
mock_status = CiStatus.DRAFT.value
mock_survey_id = "123"
mock_title = "My test survey"


class TestCiMetadata:
    """Testsfor the `CiMetadata` response model"""

    def test_to_firestore_dict_includes_sds_schema_if_filled(self):
        """
        `to_firestore_dict` method should return a dictionary including `sds_schema` field as a
        key/value pair if model is initiatised with this field as a valid string
        """
        ci_metadata = CiMetadata(
            ci_version=mock_ci_version,
            data_version=mock_data_version,
            form_type=mock_form_type,
            id=mock_id,
            language=mock_language,
            published_at=mock_published_at,
            schema_version=mock_schema_version,
            sds_schema=mock_sds_schema,
            status=mock_status,
            survey_id=mock_survey_id,
            title=mock_title,
        )

        assert "sds_schema" in ci_metadata.to_firestore_dict().keys()

        firestore_dict = ci_metadata.to_firestore_dict()
        assert firestore_dict["sds_schema"] == mock_sds_schema

    def test_to_firestore_dict_omits_sds_schema_if_not_filled(self):
        """
        `to_firestore_dict` method should return a dictionary omitting `sds_schema` field as a
        key/value pair if model is initiatised without this field
        """
        ci_metadata = CiMetadata(
            ci_version=mock_ci_version,
            data_version=mock_data_version,
            form_type=mock_form_type,
            id=mock_id,
            language=mock_language,
            published_at=mock_published_at,
            schema_version=mock_schema_version,
            status=mock_status,
            survey_id=mock_survey_id,
            title=mock_title,
        )

        assert "sds_schema" not in ci_metadata.to_firestore_dict().keys()
