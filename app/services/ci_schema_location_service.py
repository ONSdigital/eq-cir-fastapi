from app.models.responses import CiMetadata


class CiSchemaLocationService:
    @staticmethod
    def get_ci_schema_location(
        ci_metadata: CiMetadata,
    ) -> str:
        """
        Generate the ci schema location for the metadata being processed.

        Parameters:
        ci_metadata (CiMetadata): the metadata being processed.
        """
        guid = ci_metadata.guid

        return f"{guid}.json"
