import datetime
import uuid

from google.cloud import firestore

from app.config import Settings, logging
from app.models.requests import PostCiMetadataV1PostData
from app.models.responses import CiMetadata, CiStatus

logger = logging.getLogger(__name__)
settings = Settings()

db = firestore.Client(project=settings.PROJECT_ID)
ci_collection = db.collection(settings.CI_FIRESTORE_COLLECTION_NAME)


def query_latest_ci_version(survey_id, form_type, language):
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
        ci_collection.where("survey_id", "==", survey_id)
        .where("form_type", "==", form_type)
        .where("language", "==", language)
        .order_by("ci_version", direction=firestore.Query.DESCENDING)
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


def query_latest_ci_version_id(survey_id, form_type, language):
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
        ci_collection.where("survey_id", "==", survey_id)
        .where("form_type", "==", form_type)
        .where("language", "==", language)
        .order_by("ci_version", direction=firestore.Query.DESCENDING)
        .limit(1)
        .stream()
    )

    ci_id = None
    for ci in ci_versions:
        ci_id = ci.id

    logger.info("query_latest_ci_version_id successful")
    return ci_id


# Posts new CI metadata to Firestore
def post_ci_metadata(post_data: PostCiMetadataV1PostData) -> CiMetadata:
    """Creates new ci version"""

    logger.info("stepping into post_ci_metadata")
    logger.debug(f"post_ci_metadata data received: {post_data.__dict__}")

    # get latest ci version for combination of survey_id, form_type, language
    latest_ci_version = query_latest_ci_version(post_data.survey_id, post_data.form_type, post_data.language)
    new_ci_version = latest_ci_version + 1
    # Set published at to now
    published_at = datetime.datetime.utcnow().strftime(settings.PUBLISHED_AT_FORMAT)
    # Generate new uid
    uid = str(uuid.uuid4())

    ci_metadata = CiMetadata(
        ci_version=new_ci_version,
        data_version=post_data.data_version,
        form_type=post_data.form_type,
        id=uid,
        language=post_data.language,
        published_at=published_at,
        schema_version=post_data.schema_version,
        sds_schema=post_data.sds_schema,
        status=CiStatus.DRAFT.value,
        survey_id=post_data.survey_id,
        title=post_data.title,
    )

    # Add new version using `to_firestore_dict` method to generate dictionary of metadata. This
    # removes `sds_schema` key if not filled
    ci_collection.document(uid).set(ci_metadata.to_firestore_dict())
    logger.info(f"post_ci_metadata output: {ci_metadata.__dict__}")
    logger.info("post_ci_metadata success")
    return ci_metadata


def query_ci_metadata(survey_id, form_type, language, status=None):
    """
    Queries CIR with survey_id and form_id and return CI with all version_ids
    """
    logger.debug(f"data received: form_type: {form_type}, language: {language}, status: {status}, survey_id: {survey_id}")

    if status is None:
        query_result = (
            ci_collection.where("survey_id", "==", survey_id)
            .where("form_type", "==", form_type)
            .where("language", "==", language)
            .order_by("ci_version", direction=firestore.Query.DESCENDING)
            .stream()
        )
    elif status in ["DRAFT", "PUBLISHED"]:
        query_result = (
            ci_collection.where("survey_id", "==", survey_id)
            .where("form_type", "==", form_type)
            .where("language", "==", language)
            .where("status", "==", status)
            .order_by("ci_version", direction=firestore.Query.DESCENDING)
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


def update_ci_metadata_status_to_published(guid, update_json):
    """
    Updates CI with id of guid
    with json in update_json
    """
    logger.debug(
        f"update_ci_by_guid data received: {guid}",
    )

    ci_collection.document(guid).update(update_json)

    logger.info("stepping out of update_ci_by_guid")
    return


def delete_ci_metadata(survey_id):
    """
    For testing purposes only - deletes documents from remote firestore database
    :params survey_id
    """
    logger.info("delete_ci_metadata")
    logger.debug(f"data received: survey_id: {survey_id}")
    docs = ci_collection.where("survey_id", "==", survey_id).stream()

    for doc in docs:
        key = doc.id
        ci_collection.document(key).delete()
    logger.info("delete_ci_metadata_and_schema success")


def query_ci_metadata_with_guid(guid):
    """
    Queries CIR with guid
    and return CI with all version_ids
    """
    logger.info("Gets CI using guid")
    logger.debug(f"GUID received: {guid}")
    query_result = ci_collection.document(guid).get()
    logger.debug(f"query_result {query_result.to_dict()}")

    return query_result.to_dict()


def query_ci_by_status(status):
    """
    Queries CIR with status
    and return CI with status of DRAFT OR PUBLISHED
    """
    logger.debug(f"query_ci_by_status data received: {status}")

    if status in ["DRAFT", "PUBLISHED"]:
        query_result = (
            ci_collection.where("status", "==", status)
            .order_by(
                "ci_version",
                direction=firestore.Query.DESCENDING,
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


def get_all_ci_metadata():
    """
    Queries CIR with no params
    and return all CI
    """
    logger.debug("get_all_ci_metadata data received")
    query_result = ci_collection.order_by(
        "ci_version",
        direction=firestore.Query.DESCENDING,
    ).stream()
    logger.info("stepping out of get_all_ci_metadata")
    return [ci.to_dict() for ci in query_result]


def query_ci_by_survey_id(survey_id):
    """
    Queries CIR with survey_id
    and return CI
    """
    logger.debug(f"query_ci_by_survey_id data received: {survey_id}")
    query_result = (
        ci_collection.where("survey_id", "==", survey_id)
        .order_by(
            "ci_version",
            direction=firestore.Query.DESCENDING,
        )
        .stream()
    )
    logger.info("stepping out of query_ci_by_survey_id")
    return [ci.to_dict() for ci in query_result]
