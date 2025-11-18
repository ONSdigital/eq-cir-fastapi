from dataclasses import dataclass
from typing import Final

from fastapi import Query
from pydantic import BaseModel, ValidationInfo, field_validator
from pydantic.json_schema import SkipJsonSchema

from app.models.classifier import Classifiers

CLASSIFIER_TYPE_DESC: Final[str] = "classifier_type used by the CI"
CLASSIFIER_VALUE_DESC: Final[str] = "classifier_value used by the CI"
LANG_DESC: Final[str] = "The language of the CI"
SURVEY_ID_DESC: Final[str] = "The survey_id of the CI"


@dataclass
class DeleteCiV1Params:
    """Model for `delete_ci_metadata_v1` request query params"""

    survey_id: str = Query(default=None, description="The survey ID of the CI to be deleted.", example="123")


@dataclass
class GetCiMetadataV1Params:
    """Model for `get_ci_metadata_v1` request query params"""

    classifier_type: Classifiers = Query(default=None, description=CLASSIFIER_TYPE_DESC, example="form_type")
    classifier_value: str = Query(default=None, description=CLASSIFIER_VALUE_DESC, example="0001")
    language: str = Query(default=None, description=LANG_DESC, example="en")
    survey_id: str = Query(default=None, description=SURVEY_ID_DESC, example="123")

    def params_not_none(self, keys):
        """
        Loops through each input `keys` and checks if associated class param is `None`

        If all param values are not `None` return `True`, otherwise return `False`
        """
        return all(getattr(self, key) for key in keys)

@dataclass
class GetCiMetadataV2Params:
    """
    Model for `get_ci_metadata_v2` request query params
    All parameters are optional
    """

    classifier_type: Classifiers = Query(default=None, description=CLASSIFIER_TYPE_DESC, example="form_type")
    classifier_value: str = Query(default=None, description=CLASSIFIER_VALUE_DESC, example="0001")
    language: str = Query(default=None, description=LANG_DESC, example="en")
    survey_id: str = Query(default=None, description=SURVEY_ID_DESC, example="123")

    def params_not_none(self, keys):
        """
        Loops through each input `keys` and checks if associated class param is `None`

        If all param values are not `None` return `True`, otherwise return `False`
        """
        return all(getattr(self, key) for key in keys)

    def params_all_none(self, keys):
        """
        Loops through each input `keys` and checks if associated class param is `None`

        If all param values are `None` return `True`, otherwise return `False`
        """
        return all(not getattr(self, key) for key in keys)

@dataclass
class GetCiMetadataV3Params:
    """
    Model for `get_ci_metadata_v3` request query params
    All parameters are optional
    """

    guid: str = Query(default=None, description="GUID")

@dataclass
class GetCiSchemaV1Params:
    """Model for `get_ci_schema_v1` request query params"""

    classifier_type: Classifiers = Query(default=None, description=CLASSIFIER_TYPE_DESC, example="form_type")
    classifier_value: str = Query(default=None, description=CLASSIFIER_VALUE_DESC, example="0001")
    language: str = Query(default=None, description=LANG_DESC, example="en")
    survey_id: str = Query(default=None, description=SURVEY_ID_DESC, example="123")

    def params_not_none(self, *args):
        """
        Loops through each input `arg` and checks if associated class param is `None`

        If all param values are not `None` return `True`, otherwise return `False`
        """
        return all(getattr(self, arg) for arg in args)


@dataclass
class GetCiSchemaV2Params:
    """Model for `get_ci_schema_v2` request query params"""

    guid: str = Query(
        default=None,
        description="The global unique ID of the CI",
        example="428ae4d1-8e7f-4a9d-8bef-05a266bf81e7",
    )


class PostCiSchemaV1Data(BaseModel):
    """
    Model for `post_ci_schema_v1` request post data

    This is the entire CI JSON object that you would like to publish. The example below illustrates
    the required attributes to put into the request body. The POST will fail if these are not
    included.
    """

    # Required fields
    data_version: str
    language: str
    survey_id: str
    title: str
    # Optional fields (classifiers)
    form_type: str | SkipJsonSchema[None] = None
    # Optional fields (others)
    legal_basis: str | SkipJsonSchema[None] = ""
    metadata: list | SkipJsonSchema[None] = None
    mime_type: str | SkipJsonSchema[None] = ""
    navigation: dict | SkipJsonSchema[None] = None
    questionnaire_flow: dict | SkipJsonSchema[None] = None
    post_submission: dict | SkipJsonSchema[None] = None
    sds_schema: str | SkipJsonSchema[None] = ""
    sections: list | SkipJsonSchema[None] = None
    submission: dict | SkipJsonSchema[None] = None
    theme: str | SkipJsonSchema[None] = ""

    @field_validator("data_version", "language", "survey_id", "title")
    @classmethod
    def check_not_empty_string(cls, value: str, info: ValidationInfo) -> str:
        """Raise `ValueError` if input `value` is an empty string or whitespace"""
        if value == "" or value.isspace():
            raise ValueError(f"{info.field_name} can't be empty or null")
        return value


@dataclass
class PostCiSchemaV2Params:
    """Model for `post_ci_schema_v2` request query params"""

    validator_version: str = Query(default=None, description="Validator version of CI schema", example="0.0.1")

@dataclass
class PatchValidatorVersionV1Params:
    """Model for `post_ci_schema_v2` request query params"""

    guid: str = Query(default=None, description="guid for CI")
    validator_version: str = Query(default=None, description="Validator version of CI schema", example="0.0.1")

    def params_not_none(self, keys):
        """
        Loops through each input `keys` and checks if associated class param is `None`

        If all param values are not `None` return `True`, otherwise return `False`
        """
        return all(getattr(self, key) for key in keys)
