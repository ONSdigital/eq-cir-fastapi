from dataclasses import dataclass
from enum import Enum

from fastapi import Query
from pydantic import BaseModel, ValidationInfo, field_validator
from pydantic.json_schema import SkipJsonSchema

from app.models.classifier import Classifiers


class Status(Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


@dataclass
class DeleteCiV1Params:
    """Model for `delete_ci_metadata_v1` request query params"""

    survey_id: str = Query(default=None, description="The survey ID of the CI to be deleted.", example="123")


@dataclass
class GetCiMetadataV1Params:
    """Model for `get_ci_metadata_v1` request query params"""

    classifier_type: Classifiers = Query(default=None, description="Classifier type used by the CI", examples="form_type")
    classifier_value: str = Query(default=None, description="Classifier value used by the CI", examples="0001")
    language: str = Query(default=None, description="The language of the CI", example="en")
    survey_id: str = Query(default=None, description="The survey ID of the CI", example="123")

    def params_not_none(self, keys):
        """
        Loops through each input `keys` and checks if associated class param is `None`

        If all param values are not `None` return `True`, otherwise return `False`
        """
        for key in keys:
            # If value is `None`, return `False` and break out of loop
            if not getattr(self, key):
                return False

        return True


@dataclass
class GetCiMetadataV2Params:
    """
    Model for `get_ci_metadata_v2` request query params
    All parameters are optional
    """

    classifier_type: Classifiers = Query(default=None, description="Classifier type used by the CI", examples="form_type")
    classifier_value: str = Query(default=None, description="Classifier value used by the CI", examples="0001")
    language: str = Query(default=None, description="language to get", example="en")
    survey_id: str = Query(default=None, description="survey id to get", example="123")

    def params_not_none(self, keys):
        """
        Loops through each input `keys` and checks if associated class param is `None`

        If all param values are not `None` return `True`, otherwise return `False`
        """
        for key in keys:
            # If value is `None`, return `False` and break out of loop
            if not getattr(self, key):
                return False

        return True

    def params_all_none(self, keys):
        """
        Loops through each input `keys` and checks if associated class param is `None`

        If all param values are `None` return `True`, otherwise return `False`
        """
        for key in keys:
            # If value is `None`, return `False` and break out of loop
            if getattr(self, key):
                return False

        return True


@dataclass
class GetCiSchemaV1Params:
    """Model for `get_ci_schema_v1` request query params"""

    classifier_type: Classifiers = Query(default=None, description="Classifier type used by the CI", examples="form_type")
    classifier_value: str = Query(default=None, description="Classifier value used by the CI", examples="0001")
    language: str = Query(default=None, description="The language of the CI", example="en")
    survey_id: str = Query(default=None, description="The survey ID of the CI", example="123")

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
class GetCiSchemaV2Params:
    """Model for `get_ci_schema_v2` request query params"""

    guid: str = Query(
        default=None,
        description="The global unique ID of the CI",
        example="428ae4d1-8e7f-4a9d-8bef-05a266bf81e7",
    )


class PostCiMetadataV1PostData(BaseModel):
    """
    Model for `post_ci_metadata_v1` request post data

    This is the entire CI JSON object that you would like to publish. The example below illustrates
    the required attributes to put into the request body. The POST will fail if these are not
    included.
    """

    # Required fields
    data_version: str
    classifier_type: str
    classifier_value: str
    language: str
    survey_id: str
    title: str
    schema_version: str
    description: str
    # Optional fields
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

    @field_validator("data_version", "classifier_type", "classifier_value", "language", "survey_id", "title", "schema_version")
    @classmethod
    def check_not_empty_string(cls, value: str, info: ValidationInfo) -> str:
        """Raise `ValueError` if input `value` is an empty string or whitespace"""
        if value == "" or value.isspace():
            raise ValueError(f"{info.field_name} can't be empty or null")
        return value


@dataclass
class PutStatusV1Params:
    """
    Model for `put_status_v1` request params
    """

    guid: str = Query(
        default=None,
        description="The global unique ID of the CI Metadata to be updated to 'PUBLISH'.",
        example="428ae4d1-8e7f-4a9d-8bef-05a266bf81e7",
    )
