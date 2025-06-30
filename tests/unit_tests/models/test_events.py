import datetime
import uuid

from app.config import Settings
from app.models.events import PostCIEvent

settings = Settings()


# Mock data for all tests
mock_ci_version = "1"
mock_data_version = "1"
mock_validator_version = "0.0.1"
mock_classifier_type = "form_type"
mock_classifier_value = "t"
mock_id = str(uuid.uuid4())
mock_language = "em"
mock_published_at = datetime.datetime.utcnow().strftime(settings.PUBLISHED_AT_FORMAT)
mock_sds_schema = "my test schema"
mock_survey_id = "12124141"
mock_title = "test"


class TestPostCIEvent:
    """Testsfor the `PostCIEvent` response model"""

    def test_model_dump_includes_sds_schema_if_filled(self):
        """
        Overidden `model_dump` method should return a dictionary including `sds_schema` field as a
        key/value pair if model is initiatised with this field as a valid string
        """
        ci_event = PostCIEvent(
            ci_version=mock_ci_version,
            validator_version=mock_validator_version,
            data_version=mock_data_version,
            classifier_type=mock_classifier_type,
            classifier_value=mock_classifier_value,
            guid=mock_id,
            language=mock_language,
            published_at=mock_published_at,
            sds_schema=mock_sds_schema,
            survey_id=mock_survey_id,
            title=mock_title,
        )

        model_dict = ci_event.model_dump()

        assert "sds_schema" in model_dict
        assert model_dict["sds_schema"] == mock_sds_schema

    def test_model_dump_excludes_sds_schema_if_not_filled(self):
        """
        Overidden `model_dump` method should return a dictionary excluding `sds_schema` field as a
        key/value pair if model is initiatised without this field
        """
        ci_event = PostCIEvent(
            ci_version=mock_ci_version,
            validator_version=mock_validator_version,
            data_version=mock_data_version,
            classifier_type=mock_classifier_type,
            classifier_value=mock_classifier_value,
            guid=mock_id,
            language=mock_language,
            published_at=mock_published_at,
            survey_id=mock_survey_id,
            title=mock_title,
        )

        model_dict = ci_event.model_dump()

        assert "sds_schema" not in model_dict

    def test_model_dump_excludes_additional_fields_if_required(self):
        """
        Overidden `model_dump` method should return a dictionary excluding `sds_schema` field as a
        key/value pair if model is initiatised without this field. It should also be able to
        exclude additional fields if called with the `exclude` kwarg.
        """
        ci_event = PostCIEvent(
            ci_version=mock_ci_version,
            validator_version=mock_validator_version,
            data_version=mock_data_version,
            classifier_type=mock_classifier_type,
            classifier_value=mock_classifier_value,
            guid=mock_id,
            language=mock_language,
            published_at=mock_published_at,
            survey_id=mock_survey_id,
            title=mock_title,
        )
        # Include additional `published_at` exclude field
        model_dict = ci_event.model_dump(exclude={"published_at"})

        assert "sds_schema" not in model_dict
        assert "published_at" not in model_dict
