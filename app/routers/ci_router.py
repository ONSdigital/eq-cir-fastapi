from dataclasses import asdict

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.config import Settings, logging
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
from app.models.responses import BadRequest, CiMetadata, CiStatus
from app.repositories.buckets.ci_schema_bucket_repository import (
    CiSchemaBucketRepository,
)
from app.services.ci_processor_service import CiProcessorService
from app.services.ci_schema_location_service import CiSchemaLocationService

router = APIRouter()

logger = logging.getLogger(__name__)
settings = Settings()

# Definition of default response messages that can be used across all endpoints
DEFAULT_RESPONSES = {
    status.HTTP_400_BAD_REQUEST: {
        "model": BadRequest,
        "description": (
            "Bad request. This is triggered by when a bad request body is provided. The response will inform the user "
            "what required parameter they are missing from the request."
        ),
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal error. This is triggered when something an unexpected error occurs on the server side.",
    },
}

HTTP_404_NOT_FOUND_RESPONSE = {
    status.HTTP_404_NOT_FOUND: {
        "model": BadRequest,
        "description": "Bad request. This is triggered when there is no CI data that matches the request provided.",
    },
}


@router.delete(
    "/v1/dev/teardown",
    responses={
        **DEFAULT_RESPONSES,  # type: ignore [dict-item]
        **HTTP_404_NOT_FOUND_RESPONSE,  # type: ignore [dict-item]
        status.HTTP_200_OK: {
            "description": (
                "Successfully deleted a CI's schema and metadata. This is illustrated with the response informing the "
                "user of the survey_id that has been deleted."
            ),
        },
    },
)
async def http_delete_ci_v1(
    query_params: DeleteCiV1Params = Depends(),
    ci_processor_service: CiProcessorService = Depends(),
):
    """
    DELETE method that deletes the CI schema from the bucket as well as the CI metadata from Firestore.
    """
    logger.info("Deleting ci metadata and schema via v1 endpoint...")
    logger.debug(f"Input data: query_params={query_params.__dict__}")

    ci_metadata_collection = ci_processor_service.get_ci_metadata_colleciton_with_survey_id(query_params.survey_id)

    if not ci_metadata_collection:
        logger.error(f"delete_ci_v1: exception raised - No CI found for: {asdict(query_params)}")
        response_content = BadRequest(message=f"No CI found for: {asdict(query_params)}")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=asdict(response_content))

    ci_processor_service.delete_ci_in_transaction(ci_metadata_collection)

    logger.info("CI metadata and schema successfully deleted")
    response_content = f"CI metadata and schema successfully deleted for {query_params.survey_id}."
    return JSONResponse(status_code=status.HTTP_200_OK, content=response_content)


# Fetching CI Metadata from Firestore
@router.get(
    "/v1/ci_metadata",
    responses={
        **DEFAULT_RESPONSES,  # type: ignore [dict-item]
        **HTTP_404_NOT_FOUND_RESPONSE,  # type: ignore [dict-item]
        status.HTTP_200_OK: {
            "model": CiMetadata,
            "description": (
                "Successfully fetched the metadata of a CI. This is illustrated with the returned response containing the "
                "metadata of the CI."
            ),
        },
    },
)
async def http_get_ci_metadata_v1(
    query_params: GetCiMetadataV1Params = Depends(),
    ci_processor_service: CiProcessorService = Depends(),
):
    """
    GET method that returns any metadata objects from Firestore that match the parameters passed.
    """
    logger.info("Getting ci metadata via v1 endpoint...")
    logger.debug(f"Input data: query_params={query_params.__dict__}")

    ci_metadata_collection = ci_processor_service.get_ci_metadata_collection_without_status(
        query_params.survey_id, query_params.form_type, query_params.language
    )

    if not ci_metadata_collection:
        logger.info(
            f"get_ci_metadata_v1: exception raised - No CI(s) found for: {asdict(query_params)}",
        )
        response_content = BadRequest(message=f"No CI metadata found for: {asdict(query_params)}")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=asdict(response_content))

    # Call model_dump to remove optional fields that are None
    return_ci_metadata_collection = []
    for ci_metadata in ci_metadata_collection:
        return_ci_metadata_collection.append(ci_metadata.model_dump())

    logger.info("CI metadata retrieved successfully.")

    return return_ci_metadata_collection


@router.get(
    "/v2/ci_metadata",
    responses={
        **DEFAULT_RESPONSES,  # type: ignore [dict-item]
        **HTTP_404_NOT_FOUND_RESPONSE,  # type: ignore [dict-item]
        status.HTTP_200_OK: {
            "model": CiMetadata,
            "description": "Successfully Queried a CI",
        },
    },
)
async def http_get_ci_metadata_v2(
    query_params: GetCiMetadataV2Params = Depends(),
    ci_processor_service: CiProcessorService = Depends(),
):
    """
    GET method that returns any metadata objects from Firestore that match the parameters passed.
    The user has multiple ways of querying the metadata.
    1. Provide survey_id, form_type, language and status.
    2. Provide survey_id, form_type, language.
    3. Provide status.
    4. Provide no parameters.
    """
    logger.info("Getting ci metadata via v2 endpoint...")
    logger.debug(f"Input data: query_params={query_params.__dict__}")

    # Validate the status parameter
    if query_params.params_not_none("status"):
        if query_params.status.upper() not in [
            CiStatus.DRAFT.value,
            CiStatus.PUBLISHED.value,
        ]:
            logger.error(
                f"get_ci_metadata_v2: exception raised - Status is invalid in query: {asdict(query_params)}",
            )
            response_content = BadRequest(message=f"Status is invalid in query: {asdict(query_params)}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=asdict(response_content),
            )

    if query_params.params_not_none("form_type", "language", "status", "survey_id"):
        ci_metadata_collection = ci_processor_service.get_ci_metadata_collection_with_status(
            query_params.survey_id,
            query_params.form_type,
            query_params.language,
            query_params.status,
        )

    elif query_params.params_not_none("form_type", "language", "survey_id"):
        ci_metadata_collection = ci_processor_service.get_ci_metadata_collection_without_status(
            query_params.survey_id, query_params.form_type, query_params.language
        )

    elif query_params.params_not_none("status"):
        ci_metadata_collection = ci_processor_service.get_ci_metadata_collection_only_with_status(query_params.status)

    else:
        ci_metadata_collection = ci_processor_service.get_all_ci_metadata_collection()

    if not ci_metadata_collection:
        logger.info(
            f"get_ci_metadata_v2: exception raised - No CI(s) found for: {asdict(query_params)}",
        )
        response_content = BadRequest(message=f"No CI metadata found for: {asdict(query_params)}")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=asdict(response_content))

    # Call model_dump to remove optional fields that are None
    return_ci_metadata_collection = []
    for ci_metadata in ci_metadata_collection:
        return_ci_metadata_collection.append(ci_metadata.model_dump())

    logger.info("CI metadata retrieved successfully.")

    return return_ci_metadata_collection


# Fetching CI schema from Bucket version 1
@router.get(
    "/v1/retrieve_collection_instrument",
    responses={
        **DEFAULT_RESPONSES,  # type: ignore [dict-item]
        **HTTP_404_NOT_FOUND_RESPONSE,  # type: ignore [dict-item]
        status.HTTP_200_OK: {
            "model": CiMetadata,
            "description": (
                "Successfully retrieved the CI schema. This is illustrated by returning the CI schema to the user."
            ),
        },
    },
)
async def http_get_ci_schema_v1(
    query_params: GetCiSchemaV1Params = Depends(),
    ci_processor_service: CiProcessorService = Depends(),
    ci_schema_bucket_repository: CiSchemaBucketRepository = Depends(),
) -> dict:
    """
    GET method that fetches a CI schema by it's survey_id, form_type and language.
    """
    logger.info("Getting ci schema via v1 endpoint...")
    logger.debug(f"Input data: query_params={query_params.__dict__}")

    latest_ci_metadata = ci_processor_service.get_latest_ci_metadata(
        query_params.survey_id, query_params.form_type, query_params.language
    )

    if not latest_ci_metadata:
        logger.debug(
            f"get_ci_schema_v1: exception raised - No CI found for: {asdict(query_params)}",
        )
        message = f"No metadata found for: {asdict(query_params)}"
        logger.info(
            f"get_ci_schema_v1: exception raised - {message}",
        )
        response_content = BadRequest(message=message)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=asdict(response_content))

    bucket_schema_filename = CiSchemaLocationService.get_ci_schema_location(latest_ci_metadata)

    logger.debug(f"Bucket schema location: {bucket_schema_filename}")
    logger.info("Bucket schema location successfully retrieved. Getting schema...")

    ci_schema = ci_schema_bucket_repository.retrieve_ci_schema(bucket_schema_filename)

    if not ci_schema:
        logger.debug(
            f"get_ci_schema_v1: exception raised - No schema found for: {asdict(query_params)}",
        )
        message = f"No schema found for: {asdict(query_params)}"
        logger.info(
            f"get_ci_schema_v1: exception raised - {message}",
        )
        response_content = BadRequest(message=message)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=asdict(response_content))

    logger.info("Schema successfully retrieved.")

    return ci_schema


# Fetching CI schema from Bucket Version 2
@router.get(
    "/v2/retrieve_collection_instrument",
    responses={
        **DEFAULT_RESPONSES,  # type: ignore [dict-item]
        **HTTP_404_NOT_FOUND_RESPONSE,  # type: ignore [dict-item]
        status.HTTP_200_OK: {
            "model": CiMetadata,
            "description": (
                "Successfully Queried a CI. This is illustrated with the returned response containing the schema of the CI."
            ),
        },
    },
)
async def http_get_ci_schema_v2(
    query_params: GetCiSchemaV2Params = Depends(),
    ci_processor_service: CiProcessorService = Depends(),
    ci_schema_bucket_repository: CiSchemaBucketRepository = Depends(),
) -> dict:
    """
    GET method that fetches a CI schema by it's GUID.
    """
    logger.info("Getting ci schema via v2 endpoint...")
    logger.debug(f"Input data: query_params={query_params.__dict__}")

    ci_metadata = ci_processor_service.get_ci_metadata_with_id(query_params.guid)

    if not ci_metadata:
        logger.debug(
            f"get_ci_schema_v2: exception raised - No CI found for: {query_params.guid}",
        )
        message = f"No CI metadata found for: {query_params.guid}"
        logger.info(
            f"get_ci_schema_v2: exception raised - {message}",
        )
        response_content = BadRequest(message=message)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=asdict(response_content))

    bucket_schema_filename = CiSchemaLocationService.get_ci_schema_location(ci_metadata)

    logger.debug(f"Bucket schema location: {bucket_schema_filename}")
    logger.info("Bucket schema location successfully retrieved. Getting schema...")

    ci_schema = ci_schema_bucket_repository.retrieve_ci_schema(bucket_schema_filename)

    if not ci_schema:
        logger.debug(
            f"get_ci_schema_v2: exception raised - No schema found for: {query_params.guid}",
        )
        message = f"No schema found for: {query_params.guid}"
        logger.info(
            f"get_ci_schema_v2: exception raised - {message}",
        )
        response_content = BadRequest(message=message)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=asdict(response_content))

    logger.info("Schema successfully retrieved.")

    return ci_schema


@router.post(
    "/v1/publish_collection_instrument",
    responses={
        **DEFAULT_RESPONSES,  # type: ignore [dict-item]
        status.HTTP_200_OK: {
            "model": CiMetadata,
            "description": (
                "Successfully created a CI. This is illustrated with the returned response containing the metadata of the CI."
            ),
        },
    },
)
async def http_post_ci_metadata_v1(
    post_data: PostCiMetadataV1PostData,
    ci_processor_service: CiProcessorService = Depends(),
) -> CiMetadata:
    """
    POST method that creates a Collection Instrument. This will post the metadata to Firestore and
    the whole request body to a Google Cloud Bucket.
    """
    logger.info("Posting ci schema via v1 endpoint...")

    ci_metadata = ci_processor_service.process_raw_ci(post_data)

    logger.info("CI schema posted successfully")
    return JSONResponse(status_code=status.HTTP_200_OK, content=ci_metadata.model_dump())


@router.put(
    "/v1/update_status",
    responses={
        **DEFAULT_RESPONSES,  # type: ignore [dict-item]
        **HTTP_404_NOT_FOUND_RESPONSE,  # type: ignore [dict-item]
        status.HTTP_200_OK: {
            "model": CiMetadata,
            "description": (
                "Successfully set CI status to PUBLISHED. This is illustrated by the response "
                "returning the GUID of the CI metadata that has been updated."
            ),
        },
    },
)
async def http_put_status_v1(
    query_params: PutStatusV1Params = Depends(),
    ci_processor_service: CiProcessorService = Depends(),
) -> None:
    """
    PUT method that sets the status of a CI's metadata in Firestore to 'PUBLISH'.
    """
    logger.info("Updating ci status via v1 endpoint...")

    ci_metadata = ci_processor_service.get_ci_metadata_with_id(query_params.guid)

    if not ci_metadata:
        logger.debug(
            f"put_status_v1: exception raised - No CI found for: {query_params.guid}",
        )
        message = f"No CI metadata found for: {query_params.guid}"
        logger.info(
            f"put_status_v1: exception raised - {message}",
        )
        response_content = BadRequest(message=message)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=asdict(response_content))

    if ci_metadata.status == Status.PUBLISHED.value:
        logger.info("CI already set to PUBLISHED")
        message = f"CI status has already been changed to Published for {query_params.guid}."
        return JSONResponse(status_code=status.HTTP_200_OK, content=message)

    ci_processor_service.update_ci_status_with_id(query_params.guid)

    logger.info("CI status updated to Published successfully")
    message = f"CI status has been changed to Published for {query_params.guid}."
    return JSONResponse(status_code=status.HTTP_200_OK, content=message)
