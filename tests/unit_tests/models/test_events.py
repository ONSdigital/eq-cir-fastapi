import datetime
import uuid

from app.config import Settings
from app.models.events import PostCIEvent
from app.models.responses import CiStatus

settings = Settings()


# Mock data for all tests
mock_ci_version = "1"
mock_data_version = "1"
mock_form_type = "t"
mock_id = str(uuid.uuid4())
mock_language = "em"
mock_published_at = datetime.datetime.utcnow().strftime(settings.PUBLISHED_AT_FORMAT)
mock_schema_version = "12"
mock_sds_schema = "my test schema"
mock_status = CiStatus.DRAFT.value
mock_survey_id = "12124141"
mock_title = "test"


class TestPostCIEvent:
    """Tests for the `PostCIEvent` data class"""

    def test_to_event_dict_includes_sds_schema_if_filled(self):
        """
        `to_event_dict` method should return a dictionary including `sds_schema` field as a
        key/value pair if model is initiatised with this field as a valid string
        """
        ci_metadata = PostCIEvent(
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

        assert "sds_schema" in ci_metadata.to_event_dict().keys()

        firestore_dict = ci_metadata.to_event_dict()
        assert firestore_dict["sds_schema"] == mock_sds_schema

    def test_to_event_dict_omits_sds_schema_if_not_filled(self):
        """
        `to_event_dict` method should return a dictionary omitting `sds_schema` field as a
        key/value pair if model is initiatised without this field
        """
        ci_metadata = PostCIEvent(
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

        assert "sds_schema" not in ci_metadata.to_event_dict().keys()
