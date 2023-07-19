from app.config import logging
from app.models.requests import GetCiMetadataV1Params, GetCiSchemaV1Params
from app.repositories.cloud_storage import retrieve_ci_schema
from app.repositories.firestore import query_ci_metadata, query_latest_ci_version_id

logger = logging.getLogger(__name__)


def get_ci_metadata_v1(query_params: GetCiMetadataV1Params):
    """
    Handler for GET /collection_instrument
    :param query_params: GetCiMetadataParams
    :return: ci_metadata || None
    """
    logger.info("Stepping into get_ci_metadata")

    logger.debug(f"get_ci_metadata_v1 data received: {query_params.__dict__}")
    ci_metadata = query_ci_metadata(query_params.survey_id, query_params.form_type, query_params.language)
    logger.debug(f"get_ci_metadata_v1 output: {ci_metadata}")
    return ci_metadata


def get_ci_schema_v1(query_params: GetCiSchemaV1Params):
    """
    Handler for GET /collection_instrument
    :param query_params: GetCiMetadataParams
    :return: ci_metadata || None
    """
    logger.info("Stepping into get_ci_metadata")

    logger.debug(f"get_ci_schema_v1 data received: {query_params.__dict__}")
    ci_metadata_id = query_latest_ci_version_id(query_params.survey_id, query_params.form_type, query_params.language)
    ci_schema = retrieve_ci_schema(ci_metadata_id)
    logger.debug(f"get_ci_schema_v1 output: {ci_schema}")
    return ci_metadata_id, ci_schema
