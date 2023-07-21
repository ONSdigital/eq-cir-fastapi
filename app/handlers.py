from app.config import logging
from app.models.requests import GetCiMetadataV1Params, GetCiMetadataV2Params
from app.repositories.firestore import (
    get_all_ci_metadata,
    query_ci_by_status,
    query_ci_metadata,
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


def get_ci_metadata_v2(query_params: GetCiMetadataV2Params):
    """
    Handler for GET V2 of collection_instrument
    :param request: flask request object survey_id, form_type,language and status
    :return: good_response_200 || bad_request || internal_error
    """
    logger.info("Stepping into get_ci_metadata_v2")
    logger.info("Inside the Status check")
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
