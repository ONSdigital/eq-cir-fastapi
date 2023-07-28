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
class GetCiSchemaV1Params:
    """Model for `get_ci_schema_v1` request query params"""

    form_type: str = Query(description="The form type of the CI", example="0005")
    language: str = Query(description="The language of the CI", example="en")
    survey_id: str = Query(description="The survey ID of the CI", example="123")


@dataclass
class GetCiSchemaV2Params:
    """Model for `get_ci_schema_v2` request query params"""

    id: str = Query(description="The form type of the CI", example="123578")
