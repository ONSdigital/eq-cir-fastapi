from pydantic import BaseModel


class GetCiMetadataParams(BaseModel):
    """Model for `get_ci_metadata_v1` and `get_ci_metadata_v2` request query params"""

    form_type: str
    language: str
    status: str | None = None
    survey_id: str
