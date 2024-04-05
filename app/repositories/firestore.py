import datetime
import uuid

from google.cloud.firestore import Client, Query

from app.config import settings, logging
from app.models.requests import PostCiMetadataV1PostData
from app.models.responses import CiMetadata, CiStatus
from app.repositories.firebase_loader import firebase_loader
from firebase_admin import firestore
from google.cloud.firestore import Transaction
from app.repositories.cloud_storage import store_ci_schema
from app.repositories.buckets.ci_schema_bucket_repository import CiSchemaBucketRepository

logger = logging.getLogger(__name__)


class FirestoreClient:
    """Provides methods to perform actions on firestore using the google firestore client"""

    def __init__(self):
        """
        Initialises the google firestore client and sets the target collection based on
        `settings.PROJECT_ID`, `settings.FIRESTORE_DB_NAME` and `settings.CI_FIRESTORE_COLLECTION_NAME`
        """
        self.client = firebase_loader.get_client()
        self.ci_collection = firebase_loader.get_ci_collection()
        self.ci_bucket_repository = CiSchemaBucketRepository()

    def delete_ci_metadata(self, survey_id):
        """
        For testing purposes only - deletes documents from remote firestore database
        :params survey_id
        """
        logger.info("delete_ci_metadata")
        logger.debug(f"data received: survey_id: {survey_id}")

        docs = self.ci_collection.where("survey_id", "==", survey_id).stream()

        for doc in docs:
            key = doc.id
            self.ci_collection.document(key).delete()
        logger.info("delete_ci_metadata_and_schema success")

    def get_all_ci_metadata(self):
        """
        Queries CIR with no params
        and return all CI
        """
        logger.debug("get_all_ci_metadata data received")

        query_result = self.ci_collection.order_by(
            "ci_version",
            direction=Query.DESCENDING,
        ).stream()
        logger.info("stepping out of get_all_ci_metadata")
        return [ci.to_dict() for ci in query_result]

    def query_ci_by_status(self, status):
        """
        Queries CIR with status
        and return CI with status of DRAFT OR PUBLISHED
        """
        logger.debug(f"query_ci_by_status data received: {status}")

        if status in ["DRAFT", "PUBLISHED"]:
            query_result = (
                self.ci_collection.where("status", "==", status)
                .order_by(
                    "ci_version",
                    direction=Query.DESCENDING,
                )
                .stream()
            )
        else:
            # Return as empty dictionary
            query_result = {}
            logger.info(
                f"Status parameter error. Status parameter received: {status}. " "Status should either be DRAFT or PUBLISHED",
            )

        logger.info("stepping out of query_ci_by_status")
        return [ci.to_dict() for ci in query_result]

    def query_ci_by_survey_id(self, survey_id):
        """
        Queries CIR with survey_id
        and return CI
        """
        logger.debug(f"query_ci_by_survey_id data received: {survey_id}")

        query_result = (
            self.ci_collection.where("survey_id", "==", survey_id)
            .order_by(
                "ci_version",
                direction=Query.DESCENDING,
            )
            .stream()
        )
        logger.info("stepping out of query_ci_by_survey_id")
        return [ci.to_dict() for ci in query_result]

    def query_ci_metadata(self, survey_id, form_type, language, status=None):
        """
        Queries CIR with survey_id and form_id and return CI with all version_ids
        """
        logger.debug(f"data received: form_type: {form_type}, language: {language}, status: {status}, survey_id: {survey_id}")

        if status is None:
            query_result = (
                self.ci_collection.where("survey_id", "==", survey_id)
                .where("form_type", "==", form_type)
                .where("language", "==", language)
                .order_by("ci_version", direction=Query.DESCENDING)
                .stream()
            )
        elif status in ["DRAFT", "PUBLISHED"]:
            query_result = (
                self.ci_collection.where("survey_id", "==", survey_id)
                .where("form_type", "==", form_type)
                .where("language", "==", language)
                .where("status", "==", status)
                .order_by("ci_version", direction=Query.DESCENDING)
                .stream()
            )
        else:
            # Return as empty dictionary
            query_result = {}
            logger.info(
                f"Status parameter error. Status parameter received: {status}. " "Status should either be DRAFT or PUBLISHED",
            )

        logger.info("stepping out of search_multiple_ci")
        return [ci.to_dict() for ci in query_result]

    def query_ci_metadata_with_guid(self, guid):
        """
        Queries CIR with guid
        and return CI with all version_ids
        """
        logger.info("Gets CI using guid")
        logger.debug(f"GUID received: {guid}")

        query_result = self.ci_collection.document(guid).get()
        logger.debug(f"query_result {query_result.to_dict()}")

        return query_result.to_dict()

    def query_latest_ci_version(self, survey_id, form_type, language):
        """
        Get latest ci version for CIs. If not found returns 0
        :param survey_id: string
        :param form_type: string
        :param language: string
        :return: 0 or positive integer
        """
        logger.info("Stepping into query_latest_ci_version")
        logger.debug(
            f"data received: survey_id: {survey_id}, form_type: {form_type}, language: {language}",
        )
        logger.info("checking for ci_versions")

        ci_versions = (
            self.ci_collection.where("survey_id", "==", survey_id)
            .where("form_type", "==", form_type)
            .where("language", "==", language)
            .order_by("ci_version", direction=Query.DESCENDING)
            .limit(1)
            .stream()
        )
        logger.info("finished checking for ci_versions")
        ci_version = 0
        logger.info("checking number of ci_versions")
        for ci in ci_versions:
            ci_dict = ci.to_dict()
            ci_version = ci_dict["ci_version"] if ci_dict.get("ci_version") else 0
        logger.info("query_latest_ci_version successful")
        logger.debug(f"number of ci_versions: {ci_version}")

        return ci_version

    def query_latest_ci_version_id(self, survey_id, form_type, language):
        """
        Get latest ci version for CIs. If not found returns None
        :param survey_id: string
        :param form_type: string
        :param language: string
        :return: None or GUID
        """
        logger.info("Stepping into query_latest_ci_version_id")
        logger.debug(
            f"query_latest_ci_version_id data received: {survey_id}, {form_type}, {language}",
        )

        ci_versions = (
            self.ci_collection.where("survey_id", "==", survey_id)
            .where("form_type", "==", form_type)
            .where("language", "==", language)
            .order_by("ci_version", direction=Query.DESCENDING)
            .limit(1)
            .stream()
        )

        ci_id = None
        for ci in ci_versions:
            ci_id = ci.id

        logger.info("query_latest_ci_version_id successful")
        return ci_id

    def update_ci_metadata_status_to_published(self, guid, update_json):
        """
        Updates CI with id of guid
        with json in update_json
        """
        logger.debug(
            f"update_ci_by_guid data received: {guid}",
        )

        self.ci_collection.document(guid).update(update_json)

        logger.info("stepping out of update_ci_by_guid")
        return
    
    def get_latest_ci_metadata(self, survey_id, form_type, language):
        """
        Get metadata of latest CI version.

        Parameters:
        survey_id (str): the survey id of the CI metadata.
        form_type (str): the form type of the CI metadata.
        language (str): the language of the CI metadata.
        """
        latest_ci_metadata = (
            self.ci_collection.where("survey_id", "==", survey_id)
            .where("form_type", "==", form_type)
            .where("language", "==", language)
            .order_by("ci_version", direction=Query.DESCENDING)
            .limit(1)
            .stream()
        )
        
        ci_metadata: CiMetadata = None
        for returned_metadata in latest_ci_metadata:
            ci_metadata: CiMetadata = {**returned_metadata.to_dict()}

        return ci_metadata
    
    def perform_new_ci_transaction(
        self,
        ci_id: str,
        next_version_ci_metadata: CiMetadata,
        ci: dict,
        stored_ci_filename: str,
    ) -> None:
        """
        A transactional function that wrap CI creation and CI storage processes

        Parameters:
        ci_id (str): The unique id of the new CI.
        next_version_ci_metadata (CiMetadata): The CI metadata being added to firestore.
        ci (dict): The CI being stored.
        stored_ci_filename (str): Filename of uploaded json CI.
        """

        # A stipulation of the @firestore.transactional decorator is the first parameter HAS
        # to be 'transaction', but since we're using classes the first parameter is always
        # 'self'. Encapsulating the transaction within this function circumvents the issue.

        @firestore.transactional
        def post_ci_transaction_run(transaction: Transaction):
            self.create_ci_in_transaction(
                transaction, ci_id, next_version_ci_metadata
            )
            self.ci_bucket_repository.store_ci_schema(
                stored_ci_filename, ci
            )

        post_ci_transaction_run(self.client.transaction())

    def create_ci_in_transaction(
        self,
        transaction: Transaction,
        ci_id: str,
        ci_metadata: CiMetadata,
    ) -> None:
        """
        Creates a new CI metadata entry in firestore.

        Parameters:
        ci_id (str): The unique id of the new CI.
        ci_metadata (CiMetadata): The CI metadata being added to firestore.
        """
        # Add new version using `model_dump` method to generate dictionary of metadata. This
        # removes `sds_schema` key if not filled

        transaction.set(
            self.ci_collection.document(ci_id),
            ci_metadata.model_dump(),
            merge=True,
        )

    def get_ci_metadata_collection_without_status(self, survey_id: str, form_type: str, language: str
                                   ) -> list[CiMetadata]:
        """
        Gets the collection of CI metadata with a specific survey_id, form_type, language, and status.

        Parameters:
        survey_id (str): The survey id of the CI metadata being collected.
        form_type (str): The form type of the CI metadata being collected.
        language (str): The language of the CI metadata being collected.
        """
        returned_ci_metadata = (
            self.ci_collection.where("survey_id", "==", survey_id)
            .where("form_type", "==", form_type)
            .where("language", "==", language)
            .order_by("ci_version", direction=Query.DESCENDING)
            .stream()
        )

        ci_metadata_list: list[CiMetadata] = []
        for ci_metadata in returned_ci_metadata:
            metadata: CiMetadata = {**(ci_metadata.to_dict())}
            ci_metadata_list.append(metadata)

        return ci_metadata_list

    def get_ci_metadata_collection_with_status(self, survey_id: str, form_type: str, language: str, status: str
                                   ) -> list[CiMetadata]:   
        """
        Gets the collection of CI metadata with a specific survey_id, form_type, language, and status.

        Parameters:
        survey_id (str): The survey id of the CI metadata being collected.
        form_type (str): The form type of the CI metadata being collected.
        language (str): The language of the CI metadata being collected.
        status (str): The status of the CI metadata being collected.
        """
        returned_ci_metadata = (
            self.ci_collection.where("survey_id", "==", survey_id)
                .where("form_type", "==", form_type)
                .where("language", "==", language)
                .where("status", "==", status.upper())
                .order_by("ci_version", direction=Query.DESCENDING)
                .stream()
        )

        ci_metadata_list: list[CiMetadata] = []
        for ci_metadata in returned_ci_metadata:
            metadata: CiMetadata = {**(ci_metadata.to_dict())}
            ci_metadata_list.append(metadata)

        return ci_metadata_list
    
    def get_ci_metadata_collection_only_with_status(self, status: str) -> list[CiMetadata]:
        """
        Gets the collection of CI metadata with a specific status.

        Parameters:
        status (str): The status of the CI metadata being collected.
        """
        returned_ci_metadata = (
            self.ci_collection.where("status", "==", status.upper())
                .order_by("ci_version", direction=Query.DESCENDING)
                .stream()
        )

        ci_metadata_list: list[CiMetadata] = []
        for ci_metadata in returned_ci_metadata:
            metadata: CiMetadata = {**(ci_metadata.to_dict())}
            ci_metadata_list.append(metadata)

        return ci_metadata_list
    
    def get_all_ci_metadata_collection(self) -> list[CiMetadata]:
        """
        Gets the collection of all CI metadata.
        """
        returned_ci_metadata = self.ci_collection.order_by(
            "ci_version",
            direction=Query.DESCENDING,
        ).stream()

        ci_metadata_list: list[CiMetadata] = []
        for ci_metadata in returned_ci_metadata:
            metadata: CiMetadata = {**(ci_metadata.to_dict())}
            ci_metadata_list.append(metadata)

        return ci_metadata_list
    
    def get_ci_metadata_with_guid(self, guid: str) -> CiMetadata:
        """
        Gets CI metadata using guid

        Parameters:
        guid (str): The guid of the CI metadata being collected.
        """
        retrieved_ci_metadata = self.ci_collection.where("guid","==",guid).stream()

        ci_metadata: CiMetadata = None
        for returned_metadata in retrieved_ci_metadata:
            ci_metadata: CiMetadata = {**returned_metadata.to_dict()}

        return ci_metadata
    
    def update_ci_metadata_status_to_published_with_id(self, guid: str):
        """
        Updates CI status to published using guid
        """

        self.ci_collection.document(guid).update({"status": CiStatus.PUBLISHED.value})

        return


# Posts new CI metadata to Firestore
def post_ci_metadata(post_data: PostCiMetadataV1PostData) -> CiMetadata:
    """Creates new ci version"""

    logger.info("stepping into post_ci_metadata")
    logger.debug(f"post_ci_metadata data received: {post_data.__dict__}")

    firestore_client = FirestoreClient()

    # get latest ci version for combination of survey_id, form_type, language
    latest_ci_version = firestore_client.query_latest_ci_version(post_data.survey_id, post_data.form_type, post_data.language)
    new_ci_version = latest_ci_version + 1
    # Set published at to now
    published_at = datetime.datetime.utcnow().strftime(settings.PUBLISHED_AT_FORMAT)
    # Generate new uid
    uid = str(uuid.uuid4())

    ci_metadata = CiMetadata(
        ci_version=new_ci_version,
        data_version=post_data.data_version,
        form_type=post_data.form_type,
        guid=uid,
        language=post_data.language,
        published_at=published_at,
        schema_version=post_data.schema_version,
        sds_schema=post_data.sds_schema,
        status=CiStatus.DRAFT.value,
        survey_id=post_data.survey_id,
        title=post_data.title,
        description=post_data.description,
    )

    # Add new version using `model_dump` method to generate dictionary of metadata. This
    # removes `sds_schema` key if not filled
    firestore_client.ci_collection.document(uid).set(ci_metadata.model_dump())
    logger.debug(f"post_ci_metadata output: {ci_metadata.model_dump()}")
    logger.info("post_ci_metadata success")
    return ci_metadata
