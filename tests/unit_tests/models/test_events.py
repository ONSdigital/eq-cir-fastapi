import datetime
import uuid

from app.config import Settings
from app.models.events import PostCIEvent

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
mock_status = "DRAFT"
mock_survey_id = "12124141"
mock_title = "test"


class TestPostCIEvent:
    """Tests for the `PostCIEvent` data class"""

    def test_model_includes_sds_schema_field_if_provided(self):
        """
        `PostCIEvent` data model should init and return dictionary containing `sds_schema` field
        if `sds_schema` is provided on class init
        """
        event_message = PostCIEvent(
            ci_version=mock_ci_version,
            data_version=mock_data_version,
            form_type=mock_form_type,
            id=mock_id,
            language=mock_language,
            published_at=mock_published_at,
            schema_version=mock_schema_version,
            status=mock_status,
            sds_schema=mock_sds_schema,
            survey_id=mock_survey_id,
            title=mock_title,
        )

        event_message_dict = event_message.__dict__
        assert "sds_schema" in event_message_dict.keys()
        assert event_message_dict["sds_schema"] == mock_sds_schema

    def test_model_omits_sds_schema_field_if_not_provided(self):
        """
        `PostCIEvent` data model should init and return dictionary omitting `sds_schema` field if
        if `sds_schema` is provided on class init
        """
        event_message = PostCIEvent(
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

        event_message_dict = event_message.__dict__
        assert "sds_schema" not in event_message_dict.values()
