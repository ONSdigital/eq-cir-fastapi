from app.config import logging
from app.events.publisher import Publisher
from app.models.events import PostCIEvent
from app.models.requests import (
    DeleteCiV1Params,
    GetCiMetadataV1Params,
    GetCiMetadataV2Params,
    GetCiSchemaV1Params,
    GetCiSchemaV2Params,
    PostCiMetadataV1PostData,
    PutStatusV1Params,
    Status,
)
from app.models.responses import CiMetadata
from app.repositories.cloud_storage import (
    delete_ci_schema,
    retrieve_ci_schema,
    store_ci_schema,
)
from app.repositories.firestore import (
    db,
    delete_ci_metadata,
    get_all_ci_metadata,
    post_ci_metadata,
    query_ci_by_status,
    query_ci_by_survey_id,
    query_ci_metadata,
    query_ci_metadata_with_guid,
    query_latest_ci_version_id,
    update_ci_metadata_status_to_published,
)

logger = logging.getLogger(__name__)


def delete_ci_v1(query_params: DeleteCiV1Params) -> str | None:
    """
    Handler for delete /collection_instrument.
    If ci with `survey_id` found in firestore db, deletes metadata from firestore and schema from
    storage bucket
    If ci with `survey_id` not found, returns `None`
    """
    logger.info("Stepping into delete_ci")
    ci_schemas = query_ci_by_survey_id(query_params.survey_id)

    if ci_schemas:
        with db.transaction() as transaction:
            # Deleting the metadata from firestore
            delete_ci_metadata(query_params.survey_id)
            logger.info("Delete Metadata Success")
            # Deleting the schema from bucket
            delete_ci_schema(ci_schemas)
            logger.info("Delete Schema success")
            # commit the transaction
            transaction.commit()
            logger.debug("Transaction committed")
        return f"{query_params.survey_id} deleted"
    else:
        # No ci found with the input `survey_id` so return `None`
        return None


def get_ci_metadata_v1(query_params: GetCiMetadataV1Params):
    """
    Handler for GET /collection_instrument
    :param query_params: GetCiMetadataV1Params
    :return: ci_metadata || None
    """
    logger.info("Stepping into get_ci_metadata")
    logger.debug(f"get_ci_metadata_v1 data received: {query_params.__dict__}")
    ci_metadata = query_ci_metadata(query_params.survey_id, query_params.form_type, query_params.language)
    logger.debug(f"get_ci_metadata_v1 output: {ci_metadata}")
    return ci_metadata


def get_ci_metadata_v2(query_params: GetCiMetadataV2Params):
    """
    Handler for GET V2 of collection_instrument
    :param query_params: GetCiMetadataV2Params
    :return: ci_metadata
    """
    logger.info("Stepping into get_ci_metadata_v2")
    logger.debug(f"Data received: {query_params}")

    # Condition where author is requesting CIs by status with survey_id, form_type and language
    if query_params.params_not_none("form_type", "language", "status", "survey_id"):
        search_result = query_ci_metadata(
            query_params.survey_id,
            query_params.form_type,
            query_params.language,
            query_params.status,
        )
        logger.debug(
            f"search_multiple_ci output: {search_result}",
        )

    # Condition where author is requesting CIs with survey_id, form_type and language
    elif query_params.params_not_none("form_type", "language", "survey_id"):
        search_result = query_ci_metadata(
            query_params.survey_id,
            query_params.form_type,
            query_params.language,
        )
        logger.debug(
            f"search_multiple_ci output: {search_result}",
        )

    # Condition where author is requesting CIs by status ONLY
    elif query_params.params_not_none("status"):
        search_result = query_ci_by_status(
            query_params.status,
        )
        logger.debug(
            f"search_ci_by_status output: {search_result}",
        )

    # Condition where user is requesting all CIs by no parameters
    else:
        search_result = get_all_ci_metadata()
        logger.debug(
            f"get_all_ci output: {search_result}",
        )

    return search_result


def get_ci_schema_v1(query_params: GetCiSchemaV1Params):
    """
    Handler for GET /retrieve_collection_instrument
    :param query_params: GetCiSchemaV1Params
    :return: ci_metadata_id, ci_schema, || None, None
    """
    ci_metadata_id, ci_schema = None, None
    logger.info("Stepping into get_ci_schema_v1")
    logger.debug(f"get_ci_schema_v1 data received: {query_params.__dict__}")
    ci_metadata_id = query_latest_ci_version_id(query_params.survey_id, query_params.form_type, query_params.language)
    if ci_metadata_id:
        ci_schema = retrieve_ci_schema(ci_metadata_id)
        logger.debug(f"get_ci_schema_v1 output: {ci_schema}")
    return ci_metadata_id, ci_schema


def get_ci_schema_v2(query_params: GetCiSchemaV2Params):
    """
    Handler for GET /retrieve_collection_instrument V2
    :param query_params: GetCiSchemaV2Params
    :return: ci_metadata_id, ci_schema, || None, None
    """
    ci_metadata, ci_schema = None, None
    logger.info("Stepping into get_ci_schema_v2")
    logger.debug(f"get_ci_schema_v2 data received: {query_params.__dict__}")
    ci_metadata = query_ci_metadata_with_guid(query_params.guid)
    if ci_metadata:
        ci_schema = retrieve_ci_schema(query_params.guid)
        logger.debug(f"get_ci_schema_v1 output: {ci_schema}")
    return ci_metadata, ci_schema


def post_ci_metadata_v1(post_data: PostCiMetadataV1PostData) -> CiMetadata | None:
    """
    Handler for POST /collection_instrument
    """

    logger.debug(f"post_ci_v1 data received: {post_data.__dict__}")
    publisher = Publisher()

    # Unable to test the transaction rollback in tests
    # start transaction
    with db.transaction() as transaction:
        try:
            # post metadata to firestore
            ci_metadata_with_new_version = post_ci_metadata(post_data)
            logger.debug(f"New CI created: {ci_metadata_with_new_version.__dict__}")

            # put the schema in cloud storage where filename is the unique CI id
            store_ci_schema(ci_metadata_with_new_version.id, post_data.__dict__)
            logger.info("put_schema success")

            # create event message
            event_message = PostCIEvent(
                ci_version=ci_metadata_with_new_version.ci_version,
                data_version=ci_metadata_with_new_version.data_version,
                form_type=ci_metadata_with_new_version.form_type,
                id=ci_metadata_with_new_version.id,
                language=ci_metadata_with_new_version.language,
                published_at=ci_metadata_with_new_version.published_at,
                schema_version=ci_metadata_with_new_version.schema_version,
                status=ci_metadata_with_new_version.status,
                sds_schema=ci_metadata_with_new_version.sds_schema,
                survey_id=ci_metadata_with_new_version.survey_id,
                title=ci_metadata_with_new_version.title,
                description=ci_metadata_with_new_version.description,
            )
            publisher.publish_message(event_message)

            # commit the transaction
            transaction.commit()
            logger.debug("Transaction committed")

            logger.debug(f"post_ci_v1 output data: {ci_metadata_with_new_version.__dict__}")
            return ci_metadata_with_new_version
        except Exception as e:
            # if any part of the transaction fails, rollback and delete CI schema from bucket
            logger.error(f"post_ci_v1: exception raised - {e}")
            logger.error("Rolling back transaction")
            transaction.rollback()
            logger.info("Deleted schema from bucket")
            return None


def put_status_v1(query_params: PutStatusV1Params):
    """
    HANDLER for UPDATE STATUS OF Collection Instrument
    :param request : PutStatusV1Params
    :return Updated CI
    """
    logger.info("Stepping into put_status_v1")
    logger.debug(f"put_status_v1 GUID received: {query_params.__dict__}")
    ci_metadata = query_ci_metadata_with_guid(query_params.guid)
    if not ci_metadata:
        return None, False
    if ci_metadata["status"] == Status.PUBLISHED.value:
        return ci_metadata, False
    if ci_metadata["status"] == Status.DRAFT.value:
        update_ci_metadata_status_to_published(query_params.guid, {"status": Status.PUBLISHED.value})
        return ci_metadata, True
