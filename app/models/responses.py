from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema

from app.config import logging

logger = logging.getLogger(__name__)


@dataclass
class BadRequest:
    """Model for a generic bad request response"""

    message: str
    status: str = "error"


class CiMetadata(BaseModel):
    """Model for collection instrument metadata"""

    # Required fields
    ci_version: int
    data_version: str
    classifier_type: str
    classifier_value: str
    guid: str
    language: str
    published_at: str
    survey_id: str
    title: str
    description: str
    # Optional fields
    sds_schema: str | SkipJsonSchema[None] = ""

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        """
        Override default `model_dump` to return a dictionary of data suitable for posting to
        firestore and returning to the user:
        * If `sds_schema` field is filled, include this as a key in the returned dictionary
        * If `sds_schema` field is not filled or a default value, do not include this as a key in
          the returned dictionary
        """

        if not self.sds_schema:
            # Get any additional exclude fields from input `kwargs` or return empty set
            exclude_fields = kwargs.get("exclude", set())
            # Update kwargs to exclude `sds_schema` key/value pair if not filled
            exclude_fields.add("sds_schema")
            kwargs.update({"exclude": exclude_fields})

        return super().model_dump(*args, **kwargs)


@dataclass
class DeploymentStatus:
    """Model for Successful deployment response"""

    version: str
    status: str = "OK"
