from app.models.responses import CiMetadata


class CiSchemaLocationService:
    @staticmethod
    def get_ci_schema_location(
        ci_metadata: CiMetadata,
    ) -> str | None:
        """
        Generate the ci schema location for the metadata being processed.

        Parameters:
        ci_metadata (CiMetadata): the metadata being processed.
        """
        if ci_metadata is None:
            return None

        guid = ci_metadata.guid

        return f"{guid}.json"
