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
    language: str = Query(default=None, description="langauge to get", example="en")
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
class DeleteCiV1Params:
    """Model for `delete_ci_metadata_v1` request query params"""

    survey_id: str = Query(description="The survey ID of the CI to be deleted.", example="123")
