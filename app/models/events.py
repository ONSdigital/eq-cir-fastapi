from dataclasses import dataclass


@dataclass
class PostCIEvent:
    """Defines the data structure required to publish an event when a new CI has been created."""

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
    sds_schema: str | None = ""
