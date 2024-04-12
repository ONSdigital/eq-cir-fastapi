from app.config import logging, settings
from app.events.publisher import publisher
from app.models.events import PostCIEvent
from app.models.requests import PostCiMetadataV1PostData
from app.models.responses import CiMetadata, CiStatus
from app.repositories.firebase.ci_firebase_repository import CiFirebaseRepository
from app.services.ci_schema_location_service import CiSchemaLocationService
from app.services.create_guid_service import CreateGuidService
from app.services.datetime_service import DatetimeService
from app.services.document_version_service import DocumentVersionService

logger = logging.getLogger(__name__)


class CiProcessorService:
    def __init__(self) -> None:
        self.ci_firebase_repository = CiFirebaseRepository()

    # Posts new CI metadata to Firestore
    def process_raw_ci(self, post_data: PostCiMetadataV1PostData) -> CiMetadata:
        """
        Processes incoming ci

        Parameters:
        post_data (PostCiMetadataV1PostData): incoming CI metadata
        """

        # Generate new uid
        ci_id = CreateGuidService.create_guid()

        stored_ci_filename = f"{ci_id}.json"
        ci = post_data.__dict__

        next_version_ci_metadata = self.build_next_version_ci_metadata(
            ci_id,
            post_data.survey_id,
            post_data.form_type,
            post_data.language,
            post_data.data_version,
            post_data.schema_version,
            post_data.sds_schema,
            post_data.title,
            post_data.description,
        )

        stored_ci_filename = CiSchemaLocationService.get_ci_schema_location(next_version_ci_metadata)

        self.process_raw_ci_in_transaction(ci_id, next_version_ci_metadata, ci, stored_ci_filename)
        logger.debug(f"New CI created: {next_version_ci_metadata.model_dump()}")

        # create event message
        event_message = PostCIEvent(
            ci_version=next_version_ci_metadata.ci_version,
            data_version=next_version_ci_metadata.data_version,
            form_type=next_version_ci_metadata.form_type,
            guid=next_version_ci_metadata.guid,
            language=next_version_ci_metadata.language,
            published_at=next_version_ci_metadata.published_at,
            schema_version=next_version_ci_metadata.schema_version,
            status=next_version_ci_metadata.status,
            sds_schema=next_version_ci_metadata.sds_schema,
            survey_id=next_version_ci_metadata.survey_id,
            title=next_version_ci_metadata.title,
            description=next_version_ci_metadata.description,
        )

        self.try_publish_ci_metadata_to_topic(event_message)

        return next_version_ci_metadata

    def process_raw_ci_in_transaction(
        self,
        ci_id: str,
        next_version_ci_metadata: CiMetadata,
        ci: dict,
        stored_ci_filename: str,
    ):
        """
        Process the new CI by calling a transactional function that wrap the procedures
        Commit if the function is sucessful, rolling back otherwise.

        Parameters:
        ci_id (str): The unique id of the new CI.
        next_version_ci_metadata (CiMetadata): The CI metadata being added to firestore.
        ci (dict): The CI being stored.
        stored_ci_filename (str): Filename of uploaded json CI.
        """
        try:
            logger.info("Beginning CI transaction...")
            self.ci_firebase_repository.perform_new_ci_transaction(ci_id, next_version_ci_metadata, ci, stored_ci_filename)

            logger.info("CI transaction committed successfully.")
            return next_version_ci_metadata

        except Exception as e:
            logger.error(f"Performing CI transaction: exception raised: {e}")
            logger.error("Rolling back CI transaction")
            raise Exception("Error processing CI transaction")

    def build_next_version_ci_metadata(
        self,
        ci_id: str,
        survey_id: str,
        form_type: str,
        language: str,
        data_version: str,
        schema_version: str,
        sds_schema: str,
        title: str,
        description: str,
    ) -> CiMetadata:
        """
        Builds the next version of CI metadata.

        Parameters:
        ci_id (str): the guid of the metadata.
        survey_id (str): the survey id of the schema.
        form_type (str): the form type of the schema.
        language (str): the language of the schema.
        data_version (str): the data version of the schema.
        schema_version (str): the schema version of the schema.
        sds_schema (str): the sds schema of the schema.
        title (str): the title of the schema.
        description (str): the description of the schema.

        Returns:
        CiMetadata: the next version of CI metadata.
        """
        next_version_ci_metadata = CiMetadata(
            guid=ci_id,
            ci_version=self.calculate_next_ci_version(survey_id, form_type, language),
            data_version=data_version,
            form_type=form_type,
            language=language,
            published_at=str(DatetimeService.get_current_date_and_time().strftime(settings.PUBLISHED_AT_FORMAT)),
            schema_version=schema_version,
            sds_schema=sds_schema,
            status=CiStatus.DRAFT.value,
            survey_id=survey_id,
            title=title,
            description=description,
        )
        return next_version_ci_metadata

    def calculate_next_ci_version(self, survey_id: str, form_type: str, language: str) -> int:
        """
        Calculates the next schema version for the metadata being built.

        Parameters:
        survey_id (str): the survey id of the schema.
        """

        current_version_metadata = self.ci_firebase_repository.get_latest_ci_metadata(survey_id, form_type, language)

        return DocumentVersionService.calculate_ci_version(current_version_metadata)

    def try_publish_ci_metadata_to_topic(self, next_version_ci_metadata: CiMetadata) -> None:
        """
        Publish CI metadata to pubsub topic

        Parameters:
        next_version_ci_metadata (CiMetadata): the CI metadata of the newly published CI
        """
        try:
            logger.info("Publishing CI metadata to topic...")
            publisher.publish_message(next_version_ci_metadata)
            logger.debug(f"CI metadata {next_version_ci_metadata} published to topic")
            logger.info("CI metadata published successfully.")
        except Exception as e:
            logger.debug(f"CI metadata {next_version_ci_metadata} failed to publish to topic with error {e}")
            logger.error("Error publishing CI metadata to topic.")
            raise Exception("Error publishing CI metadata to topic.")

    def get_ci_metadata_collection_without_status(self, survey_id: str, form_type: str, language: str) -> list[CiMetadata]:
        """
        Get a list of CI metadata without status

        Parameters:
        survey_id (str): the survey id of the schemas.
        form_type (str): the form type of the schemas.
        language (str): the language of the schemas.

        Returns:
        List of CiMetadata: the list CI metadata of the requested CI
        """
        logger.info("Retrieving CI metadata without status...")

        ci_metadata_collection = self.ci_firebase_repository.get_ci_metadata_collection_without_status(
            survey_id, form_type, language
        )

        return ci_metadata_collection

    def get_ci_metadata_collection_with_status(
        self, survey_id: str, form_type: str, language: str, status: str
    ) -> list[CiMetadata]:
        """
        Get a list of CI metadata with status

        Parameters:
        survey_id (str): the survey id of the schemas.
        form_type (str): the form type of the schemas.
        language (str): the language of the schemas.
        status (str): the status of the schemas.

        Returns:
        List of CiMetadata: the list CI metadata of the requested CI
        """
        logger.info("Retrieving CI metadata with status...")

        ci_metadata_collection = self.ci_firebase_repository.get_ci_metadata_collection_with_status(
            survey_id, form_type, language, status
        )

        return ci_metadata_collection

    def get_ci_metadata_collection_only_with_status(self, status: str) -> list[CiMetadata]:
        """
        Get a list of CI metadata only with status

        Parameters:
        status (str): the status of the schemas.

        Returns:
        List of CiMetadata: the list CI metadata of the requested CI
        """
        logger.info("Retrieving CI metadata only with status...")

        ci_metadata_collection = self.ci_firebase_repository.get_ci_metadata_collection_only_with_status(status)

        return ci_metadata_collection

    def get_all_ci_metadata_collection(self) -> list[CiMetadata]:
        """
        Get a list of all CI metadata

        Returns:
        List of CiMetadata: the list CI metadata of all CI
        """
        logger.info("Retrieving all CI metadata...")

        ci_metadata_collection = self.ci_firebase_repository.get_all_ci_metadata_collection()

        return ci_metadata_collection

    def get_latest_ci_metadata(self, survey_id: str, form_type: str, language: str) -> CiMetadata:
        """
        Get the latest CI metadata

        Parameters:
        survey_id (str): the survey id of the schemas.
        form_type (str): the form type of the schemas.
        language (str): the language of the schemas.

        Returns:
        str: the latest CI schema id
        """
        logger.info("Getting latest CI metadata...")

        latest_ci_metadata = self.ci_firebase_repository.get_latest_ci_metadata(survey_id, form_type, language)

        return latest_ci_metadata

    def get_ci_metadata_with_id(self, guid: str) -> CiMetadata:
        """
        Get a CI metadata with id

        Parameters:
        query_params (GetCiSchemaV2Params): incoming CI metadata query parameters

        Returns:
        CiMetadata: the CI metadata of the requested CI
        """
        logger.info("Getting CI metadata with id...")

        ci_metadata = self.ci_firebase_repository.get_ci_metadata_with_id(guid)

        return ci_metadata

    def update_ci_status_with_id(self, guid: str) -> None:
        """
        HANDLER for UPDATE STATUS OF Collection Instrument

        Parameters:
        """
        logger.info("Updating CI status with id...")

        self.ci_firebase_repository.update_ci_metadata_status_to_published_with_id(guid)

    def get_ci_metadata_colleciton_with_survey_id(self, survey_id: str) -> list[CiMetadata]:
        """
        Get CI metadata collection with survey_id

        Parameters:
        survey_id (str): the survey id of the schemas.

        Returns:
        List of CiMetadata: the list CI metadata of the requested CI
        """
        logger.info("Deleting CI metadata and schema by survey_id...")

        ci_metadata_collection = self.ci_firebase_repository.get_ci_metadata_collection_with_survey_id(survey_id)

        return ci_metadata_collection

    def delete_ci_in_transaction(self, ci_metadata_collection: list[CiMetadata]) -> None:
        """
        Delete CI by calling a transactional function that wrap the procedures

        Parameters:
        ci_metadata_collection (list[CiMetadata]): The CI metadata being deleted.
        """
        try:
            logger.info("Beginning delete CI transaction...")
            self.ci_firebase_repository.perform_delete_ci_transaction(ci_metadata_collection)

            logger.info("Delete CI transaction committed successfully.")

        except Exception as e:
            logger.error(f"Performing delete CI transaction: exception raised: {e}")
            logger.error("Rolling back CI transaction")
            raise Exception("Error processing delete CI transaction")
