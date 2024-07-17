import uuid

from app.config import Settings
from app.models.classifier import Classifiers
from app.models.requests import PostCiMetadataV1PostData, PostCiSchemaV1Data
from app.models.responses import CiMetadata

settings = Settings()


# Mock data for all tests
mock_data_version = "test_data_version"
mock_classifier_type = Classifiers.FORM_TYPE
mock_classifier_value = "test_form_type"
mock_id = str(uuid.uuid4())
mock_next_version_id = str(uuid.uuid4())
mock_language = "test_language"
mock_schema_version = "test_schema_version"
mock_sds_schema = ""
mock_survey_id = "test_survey_id"
mock_title = "test_title"
mock_description = "test_description"
mock_published_at = "2023-04-20T12:00:00.000000Z"

mock_post_ci_schema = PostCiSchemaV1Data(
    survey_id=mock_survey_id,
    language=mock_language,
    form_type=mock_classifier_value,
    title=mock_title,
    schema_version=mock_schema_version,
    data_version=mock_data_version,
    sds_schema=mock_sds_schema,
    description=mock_description,
)

mock_post_ci_schema_without_sds_schema = PostCiSchemaV1Data(
    survey_id=mock_survey_id,
    classifier_type=mock_classifier_type,
    classifier_value=mock_classifier_value,
    language=mock_language,
    title=mock_title,
    schema_version=mock_schema_version,
    data_version=mock_data_version,
    description=mock_description,
)

mock_post_ci_schema_with_sds_schema = PostCiSchemaV1Data(
    survey_id=mock_survey_id,
    language=mock_language,
    classifier_type=mock_classifier_type,
    classifier_value=mock_classifier_value,
    title=mock_title,
    schema_version=mock_schema_version,
    data_version=mock_data_version,
    sds_schema="0004",
    description=mock_description,
)

mock_ci_metadata = CiMetadata(
    ci_version=1,
    data_version=mock_data_version,
    classifier_type=mock_classifier_type,
    classifier_value=mock_classifier_value,
    guid=mock_id,
    language=mock_language,
    published_at=mock_published_at,
    schema_version=mock_schema_version,
    sds_schema=mock_sds_schema,
    survey_id=mock_survey_id,
    title=mock_title,
    description=mock_description,
)

mock_next_version_ci_metadata = CiMetadata(
    ci_version=2,
    data_version=mock_data_version,
    classifier_type=mock_classifier_type,
    classifier_value=mock_classifier_value,
    guid=mock_next_version_id,
    language=mock_language,
    published_at=mock_published_at,
    schema_version=mock_schema_version,
    sds_schema=mock_sds_schema,
    survey_id=mock_survey_id,
    title=mock_title,
    description=mock_description,
)

mock_ci_metadata_list = [
    CiMetadata(
        ci_version=1,
        data_version=mock_data_version,
        classifier_type=mock_classifier_type,
        classifier_value=mock_classifier_value,
        guid=mock_id,
        language=mock_language,
        published_at=mock_published_at,
        schema_version=mock_schema_version,
        sds_schema=mock_sds_schema,
        survey_id=mock_survey_id,
        title="test_1",
        description=mock_description,
    ),
    CiMetadata(
        ci_version=2,
        data_version=mock_data_version,
        classifier_type=mock_classifier_type,
        classifier_value=mock_classifier_value,
        guid=mock_id,
        language=mock_language,
        published_at=mock_published_at,
        schema_version=mock_schema_version,
        sds_schema=mock_sds_schema,
        survey_id=mock_survey_id,
        title="test_2",
        description=mock_description,
    ),
]

mock_ci_published_metadata = CiMetadata(
    ci_version=1,
    data_version=mock_data_version,
    classifier_type=mock_classifier_type,
    classifier_value=mock_classifier_value,
    guid=mock_id,
    language=mock_language,
    published_at=mock_published_at,
    schema_version=mock_schema_version,
    sds_schema=mock_sds_schema,
    survey_id=mock_survey_id,
    title=mock_title,
    description=mock_description,
)
