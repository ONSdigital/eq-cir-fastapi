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

    def to_event_dict(self) -> dict:
        """
        Returns a dictionary of data suitable for publishing to pub/sub:
        * If `sds_schema` field is filled, include this as a key in the returned dictionary
        * If `sds_schema` field is not filled or a default value, do not include this as a key in
          the returned dictionary
        """
        if self.sds_schema:
            return self.__dict__
        else:
            # If `sds_schema` not filled, return a dict without this key/value pair
            return {
                "ci_version": self.ci_version,
                "data_version": self.data_version,
                "form_type": self.form_type,
                "id": self.id,
                "language": self.language,
                "published_at": self.published_at,
                "schema_version": self.schema_version,
                "status": self.status,
                "survey_id": self.survey_id,
                "title": self.title,
            }
