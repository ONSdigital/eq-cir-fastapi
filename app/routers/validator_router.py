
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

import app.exception.exception_response_models as erm
from app.config import Settings, logging
from app.exception import exceptions
from app.exception.exception_response_models import ExceptionResponseModel
from app.models.requests import (
    PatchValidatorVersionV1Params,
)
from app.models.responses import CiMetadata
from app.services.ci_processor_service import CiProcessorService

router = APIRouter()

logger = logging.getLogger(__name__)
settings = Settings()


# Fetching CI schema from Bucket Version 2
@router.patch(
    "/v1/update_validator_version",
    responses={
        200: {
            "model": CiMetadata,
            "description": (
                    "Successfully Queried a CI. This is illustrated with the returned response containing the schema of the CI."
            ),
        },
        500: {
            "model": ExceptionResponseModel,
            "content": {"application/json": {"example": erm.erm_500_global_exception}},
        },
        404: {
            "model": ExceptionResponseModel,
            "content": {"application/json": {"example": erm.erm_404_no_ci_exception}},
        },
        400: {
            "model": ExceptionResponseModel,
            "content": {"application/json": {"example": erm.erm_400_incorrect_key_names_exception}},
        },
    },
)
async def http_patch_ci_validator_version_v1(
        query_params: PatchValidatorVersionV1Params = Depends(),
        ci_processor_service: CiProcessorService = Depends(),
):
    """
    PATCH method that updates validator_version by Guid.
    """
    logger.info("Patching validator_version")
    logger.info(f"Input data: query_params={query_params.__dict__}")

    if not query_params.params_not_none(query_params.__dict__.keys()):
        raise exceptions.ExceptionIncorrectKeyNames

    ci_metadata = ci_processor_service.get_ci_metadata_with_id(query_params.guid)

    if not ci_metadata:
        error_message = "patch_ci_validator: exception raised - No collection instrument metadata found"
        logger.error(error_message)
        logger.debug(f"{error_message}:{query_params.guid}")
        raise exceptions.ExceptionNoCIMetadata

    ci_metadata.validator_version = query_params.validator_version

    ci_processor_service.update_ci_validator_version(query_params.guid, ci_metadata)

    logger.info("Metadata successfully updated with new validator_version")
    logger.debug("Metadata {%1} successfully updated with validator_version: {%2}",
                 [query_params.guid, query_params.validator_version])

    return JSONResponse(status_code=status.HTTP_200_OK, content="")
