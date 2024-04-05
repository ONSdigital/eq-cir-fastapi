import uuid
from datetime import datetime

from app.config import settings, logging
from app.models.requests import (
    PostCiMetadataV1PostData, 
    GetCiMetadataV1Params, 
    GetCiMetadataV2Params,
    GetCiSchemaV1Params
)
from app.models.responses import CiMetadata, CiStatus
from app.services.document_version_service import DocumentVersionService
from app.events.publisher import publisher
from app.models.events import PostCIEvent
from app.repositories.firestore import FirestoreClient

logger = logging.getLogger(__name__)

class CiProcessorService:
    def __init__(self) -> None:
        self.ci_firebase_repository = FirestoreClient()

    # Posts new CI metadata to Firestore
    def process_raw_ci(self, post_data: PostCiMetadataV1PostData) -> CiMetadata:
        """
        Processes incoming ci

        Parameters:
        post_data (PostCiMetadataV1PostData): incoming CI metadata
        """

        # Generate new uid
        ci_id = str(uuid.uuid4())

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

        self.process_raw_ci_in_transaction(
            ci_id, next_version_ci_metadata, ci, stored_ci_filename
        )
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
            self.ci_firebase_repository.perform_new_ci_transaction(
                ci_id, next_version_ci_metadata, ci, stored_ci_filename
            )

            logger.info("CI transaction committed successfully.")
            return next_version_ci_metadata
        except Exception as e:
            logger.error(f"Performing CI transaction: exception raised: {e}")
            logger.error("Rolling back CI transaction")
            raise  # exceptions.GlobalException

    
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
            published_at=datetime.now().strftime(settings.PUBLISHED_AT_FORMAT),
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

        return DocumentVersionService.calculate_survey_version(
            current_version_metadata, "ci_version"
        )
    
    def try_publish_ci_metadata_to_topic(
        self, next_version_ci_metadata: CiMetadata
    ) -> None:
        """
        Publish CI metadata to pubsub topic

        Parameters:
        next_version_ci_metadata (CiMetadata): the CI metadata of the newly published CI
        """
        try:
            logger.info("Publishing CI metadata to topic...")
            publisher.publish_message(
                next_version_ci_metadata
            )
            logger.debug(
                f"CI metadata {next_version_ci_metadata} published to topic"
            )
            logger.info("CI metadata published successfully.")
        except Exception as e:
            logger.debug(
                f"CI metadata {next_version_ci_metadata} failed to publish to topic with error {e}"
            )
            logger.error("Error publishing CI metadata to topic.")
            raise #exceptions.GlobalException

    # For Get CI Metadata V1 and V2 endpoints
    def get_ci_metadata_collection_without_status(self, query_params: GetCiMetadataV1Params) -> list[CiMetadata]:
        """
        Get a list of CI metadata without status

        Parameters:
        query_params (GetCiMetadataV1Params): incoming CI metadata query parameters
        
        Returns:
        List of CiMetadata: the list CI metadata of the requested CI
        """
        logger.info("Retrieving CI metadata without status...")
        logger.debug(f"query parameters: {query_params.__dict__}")

        ci_metadata = self.ci_firebase_repository.get_ci_metadata_collection_without_status(query_params.survey_id, query_params.form_type, query_params.language)

        return ci_metadata
    
    # For Get CI Metadata endpoint
    def get_ci_metadata_collection_with_status(self, query_params: GetCiMetadataV2Params) -> list[CiMetadata]:
        """
        Get a list of CI metadata with status

        Parameters:
        query_params (GetCiMetadataV2Params): incoming CI metadata query parameters
        
        Returns:
        List of CiMetadata: the list CI metadata of the requested CI
        """
        logger.info("Retrieving CI metadata V2 with status...")
        logger.debug(f"query parameters: {query_params.__dict__}")

        ci_metadata = self.ci_firebase_repository.get_ci_metadata_collection_with_status(query_params.survey_id, query_params.form_type, query_params.language, query_params.status)

        return ci_metadata
    
    # For Get CI Metadata endpoint
    def get_ci_metadata_collection_only_with_status(self, status: str) -> list[CiMetadata]:
        """
        Get a list of CI metadata only with status

        Parameters:
        query_params (GetCiMetadataV2Params): incoming CI metadata query parameters
        
        Returns:
        List of CiMetadata: the list CI metadata of the requested CI
        """
        logger.info("Retrieving CI metadata only with status...")
        logger.debug(f"query parameters: status: {status}")

        ci_metadata = self.ci_firebase_repository.get_ci_metadata_collection_only_with_status(status)

        return ci_metadata
    
    # For Get CI Metadata endpoint
    def get_all_ci_metadata_collection(self) -> list[CiMetadata]:
        """
        Get a list of all CI metadata

        Returns:
        List of CiMetadata: the list CI metadata of all CI
        """
        logger.info("Retrieving all CI metadata...")

        ci_metadata = self.ci_firebase_repository.get_all_ci_metadata_collection()

        return ci_metadata
    
    
    def get_latest_ci_schema_id(self, query_params: GetCiSchemaV1Params) -> None|str:
        """
        Get the latest CI schema id

        Parameters:
        query_params (GetCiSchemaV1Params): incoming CI schema query parameters

        Returns:
        str: the latest CI schema id
        """
        logger.info("Stepping into get_ci_schema_v1")
        logger.debug(f"get_ci_schema_v1 data received: {query_params.__dict__}")

        ci_latest_ci_metadata = self.ci_firebase_repository.get_latest_ci_metadata(
            query_params.survey_id, query_params.form_type, query_params.language
        )

        if not ci_latest_ci_metadata:
            return None

        return ci_latest_ci_metadata["guid"]
