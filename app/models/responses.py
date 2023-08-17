from dataclasses import dataclass
from enum import Enum

from app.config import logging

logger = logging.getLogger(__name__)


@dataclass
class BadRequest:
    """Model for a generic bad request response"""

    message: str
    status: str = "error"


@dataclass
class CiMetadata:
    """Model for collection instrument metadata"""

    # Required fields
    ci_version: int
    data_version: str
    form_type: str
    id: str
    language: str
    published_at: str
    schema_version: str
    status: str
    survey_id: str
    title: str
    description: str
    # Optional fields
    sds_schema: str | None = ""


class CiStatus(Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
