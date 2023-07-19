from dataclasses import dataclass

from fastapi import Query


@dataclass
class GetCiMetadataV1Params:
    """Model for `get_ci_metadata_v1` request query params"""

    form_type: str = Query(description="The form type of the CI", example="0005")
    language: str = Query(description="The language of the CI", example="en")
    survey_id: str = Query(description="The survey ID of the CI", example="123")


@dataclass
class GetCiMetadataV2Params:
    """
    Model for `get_ci_metadata_v2` request query params

    All parameters are optional
    """

    form_type: str = Query(default=None, description="form type to get", example="0005")
    language: str = Query(default=None, description="langugage to get", example="en")
    status: str = Query(default=None, description="status to get", example="draft")
    survey_id: str = Query(default=None, description="survey id to get", example="123")
