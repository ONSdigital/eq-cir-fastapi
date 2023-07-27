from dataclasses import dataclass
from enum import Enum

from fastapi import Query


@dataclass
class GetCiMetadataV1Params:
    """Model for `get_ci_metadata_v1` request query params"""

    form_type: str = Query(description="The form type of the CI", example="0005")
    language: str = Query(description="The language of the CI", example="en")
    survey_id: str = Query(description="The survey ID of the CI", example="123")


@dataclass
class PostCiMetadataV1Params:
    """Model for `post_ci_metadata_v1` request query params"""

    survey_id: str = Query(description="The survey id of the CI", example="0005")
    language: str = Query(description="The language of the CI", example="en")
    form_type: str = Query(description="The form type of the CI", example="123")
    title: str = Query(description="The title of the CI", example="123")
    schema_version: str = Query(description="The schema version of the CI", example="123")
    data_version: str = Query(description="The data version of the CI", example="123")
    sds_schema: str = Query(description="The sds schema version of the CI", example="123")


class Status(Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


@dataclass
class DeleteCiV1Params:
    """Model for `delete_ci_metadata_v1` request query params"""

    survey_id: int = Query(description="The survey id of the CI", example="0005")
