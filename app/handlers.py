from app.config import logging
from app.models.requests import GetCiMetadataV1Params, DeleteCiV1Params, PostCiMetadataV1Params, Status
from app.models.responses import BadRequest
from app.repositories.cloud_storage import delete_ci_schema, store_ci_schema
from app.repositories.firestore import (
    query_ci_metadata,
    query_ci_by_survey_id,
    delete_ci_metadata,
    db,
    post_ci_metadata,
    query_latest_ci_version,
)

logger = logging.getLogger(__name__)


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


def delete_ci_v1(query_params: DeleteCiV1Params):
    """
    Handler for delete /collection_instrument
    """
    logger.info("Stepping into delete_ci")
    survey_id = query_params.survey_id
    if survey_id.isnumeric():
        ci_schemas = query_ci_by_survey_id(query_params.survey_id)
        with db.transaction() as transaction:
            # Deleting the metadata from firestore
            delete_ci_metadata(query_params.survey_id)
            logger.info("Delete Metedata Success")
            # Deleting the schema from bucket
            delete_ci_schema(ci_schemas)
            logger.info("Delete Schema success")
            # commit the transaction
            transaction.commit()
            logger.debug("Transaction committed")
        return f"{query_params.survey_id} deleted", 200
    else:
        raise ValueError("Survey ID must be an integer")


def post_ci_v1(query_params: PostCiMetadataV1Params):
    logger.info("post_ci_v1")
    """
    Handler for POST /collection_instrument
    """

    logger.debug(f"post_ci_v1 data received: {query_params}")

    ci_metadata = query_params

    logger.debug(f"post_ci_v1 CollectionInstrument output: {ci_metadata}")

    # add status with default DRAFT value
    ci_metadata.status = Status.DRAFT.value

    # get latest ci version for combination of survey_id, form_type, language
    ci_metadata.ci_version = (
        query_latest_ci_version(
            ci_metadata.survey_id,
            ci_metadata.form_type,
            ci_metadata.language,
        )
        + 1
    )
    logger.debug(f"CI latest version received: {ci_metadata.ci_version}")

    # Unable to test the transaction rollback in tests
    # start transaction
    with db.transaction() as transaction:
        try:
            # post metadata to firestore
            ci_metadata_with_new_version = post_ci_metadata(ci_metadata)
            logger.debug(f"New CI created: {ci_metadata_with_new_version.to_dict()}")

            # put the schema in cloud storage where filename is the unique CI id
            store_ci_schema(ci_metadata_with_new_version.id, query_params)
            logger.info("put_schema success")

            # commit the transaction
            transaction.commit()
            logger.debug("Transaction committed")

            logger.debug(f"post_ci_v1 output data: {ci_metadata_with_new_version.to_dict()}")
            return (ci_metadata_with_new_version.to_dict()), 200
        except Exception as e:
            # if any part of the transaction fails, rollback and delete CI schema from bucket
            logger.error(f"post_ci_v1: exception raised - {e}")
            logger.error("Rolling back transaction")
            transaction.rollback()
            logger.info("Deleted schema from bucket")
            return BadRequest("Something went wrong"), 500
