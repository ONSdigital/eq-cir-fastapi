from app.config import logging
from app.models.requests import GetCiMetadataV1Params, DeleteCiV1Params
from app.repositories.cloud_storage import delete_ci_schema
from app.repositories.firestore import query_ci_metadata, query_ci_by_survey_id, delete_ci_metadata, \
    db

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
    Handler for Delete
    """
    logger.info("Stepping into delete_ci")
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
    return ci_schemas

