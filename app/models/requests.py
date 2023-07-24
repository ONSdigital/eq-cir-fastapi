from dataclasses import dataclass

from fastapi import Query


@dataclass
class GetCiMetadataV1Params:
    """Model for `get_ci_metadata_v1` request query params"""

    form_type: str = Query(description="The form type of the CI", example="0005")
    language: str = Query(description="The language of the CI", example="en")
    survey_id: str = Query(description="The survey ID of the CI", example="123")





@dataclass
class DeleteCiMetadataV1Params:
    """Model for `delete_ci_metadata_v1` request query params"""

    survey_id: str = Query(description="The survey id of the CI", example="0005")