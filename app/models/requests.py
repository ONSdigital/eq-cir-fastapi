from dataclasses import dataclass
from enum import Enum

from fastapi import Query


class Status(Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


@dataclass
class DeleteCiV1Params:
    """Model for `delete_ci_metadata_v1` request query params"""

    survey_id: str = Query(description="The survey ID of the CI to be deleted.", examples=["123"])


@dataclass
class GetCiMetadataV1Params:
    """Model for `get_ci_metadata_v1` request query params"""

    form_type: str = Query(description="The form type of the CI", examples=["0005"])
    language: str = Query(description="The language of the CI", examples=["en"])
    survey_id: str = Query(description="The survey ID of the CI", examples=["123"])


@dataclass
class GetCiMetadataV2Params:
    """
    Model for `get_ci_metadata_v2` request query params
    All parameters are optional
    """

    form_type: str = Query(default=None, description="form type to get", examples=["0005"])
    language: str = Query(default=None, description="language to get", examples=["en"])
    status: str = Query(default=None, description="status to get", examples=["draft"])
    survey_id: str = Query(default=None, description="survey id to get", examples=["123"])

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

    form_type: str = Query(description="The form type of the CI", examples=["0005"])
    language: str = Query(description="The language of the CI", examples=["en"])
    survey_id: str = Query(description="The survey ID of the CI", examples=["123"])


@dataclass
class GetCiSchemaV2Params:
    """Model for `get_ci_schema_v2` request query params"""

    id: str = Query(description="The form type of the CI", examples=["123578"])


@dataclass
class PostCiMetadataV1PostData:
    """
    Model for `post_ci_metadata_v1` request post data

    This is the entire CI JSON object that you would like to publish. The example below illustrates
    the required attributes to put into the request body. The POST will fail if these are not
    included.
    """

    # Required fields
    data_version: str
    form_type: str
    language: str
    survey_id: str
    title: str
    schema_version: str
    # Optional fields
    legal_basis: str | None = ""
    metadata: list | None = None
    mime_type: str | None = ""
    navigation: dict | None = None
    questionnaire_flow: dict | None = None
    post_submission: dict | None = None
    sds_schema: str | None = ""
    sections: list | None = None
    submission: dict | None = None
    theme: str | None = ""


@dataclass
class PutStatusV1Params:
    """
    Model for `put_status_v1` request params
    """

    id: str = Query(
        description="The global unique ID of the CI Metadata to be updated to 'PUBLISH'.",
        examples=["428ae4d1-8e7f-4a9d-8bef-05a266bf81e7"],
    )
