from dataclasses import dataclass

from app.config import logging

logger = logging.getLogger(__name__)


@dataclass
class BadRequest:
    """Model for a generic bad request response"""

    message: str = "No CI {metadata/schema} found for {parameters}"
    status: str = "error"


@dataclass
class CiMetadata:
    """Model for collection instrument metadata"""

    ci_version: int
    data_version: str
    form_type: str
    id: str
    langugage: str
    published_at: str
    schema_version: str
    sds_schema: str
    status: str
    survey_id: str
    title: str
