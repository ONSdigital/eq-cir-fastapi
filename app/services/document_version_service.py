from app.models.responses import CiMetadata


class DocumentVersionService:
    @staticmethod
    def calculate_ci_version(
        document_current_version: CiMetadata | None,
    ) -> int:
        """Calculates the next version number of a document based on a version key, returning 1 by default if no document exists.

        Parameters:
        document_current_version: document that the version is being calculated from
        """
        if document_current_version is None:
            return 1

        if document_current_version.ci_version is None:
            raise RuntimeError("Document must contain version key")

        return document_current_version.ci_version + 1
