from dataclasses import dataclass

from fastapi import Query


@dataclass
class GetCiMetadataV1Params:
    """Model for `get_ci_metadata_v1` request query params"""

    form_type: str = Query(description="The form type of the CI", example="0005")
    language: str = Query(description="The language of the CI", example="en")
    survey_id: str = Query(description="The survey ID of the CI", example="123")


@dataclass
class GetCiSchemaV1Params:
    """Model for `get_ci_schema_v1` request query params"""

    form_type: str = Query(description="The form type of the CI", example="0005")
    language: str = Query(description="The language of the CI", example="en")
    survey_id: str = Query(description="The survey ID of the CI", example="123")


@dataclass
class GetCiSchemaV2Params:
    """Model for `get_ci_schema_v2` request query params"""

    id: str = Query(description="The form type of the CI", example="123578")
