from dataclasses import dataclass
from enum import Enum

from fastapi import Query


@dataclass
class GetCiMetadataV1Params:
    """Model for `get_ci_metadata_v1` request query params"""

    form_type: str = Query(description="The form type of the CI", example="0005")
    language: str = Query(description="The language of the CI", example="en")
    survey_id: str = Query(description="The survey ID of the CI", example="123")

class GetCiMetadataV2Params:
    """
    Model for `get_ci_metadata_v2` request query params
    All parameters are optional
    """

    form_type: str = Query(default=None, description="form type to get", example="0005")
    language: str = Query(default=None, description="langugage to get", example="en")
    status: str = Query(default=None, description="status to get", example="draft")
    survey_id: str = Query(default=None, description="survey id to get", example="123")

    def params_not_none(self, *args):
        """
        Loops through each input `arg` and checks if associated class param is `None`

        If all param values are not `None` return `True`, otherwise return `False`
        """
        for arg in args:
            # If value is `None`, return `False` and break out of loop
            if not getattr(self, arg):
                return False

        return True

      
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

