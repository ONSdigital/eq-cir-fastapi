from dataclasses import asdict

from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import Settings, logging
from app.handlers import (
    delete_ci_v1,
    get_ci_metadata_v1,
    get_ci_metadata_v2,
    get_ci_schema_v1,
    get_ci_schema_v2,
    post_ci_metadata_v1,
    put_status_v1,
)
from app.models.requests import (
    DeleteCiV1Params,
    GetCiMetadataV1Params,
    GetCiMetadataV2Params,
    GetCiSchemaV1Params,
    GetCiSchemaV2Params,
    PostCiMetadataV1PostData,
    PutStatusV1Params,
)
from app.models.responses import BadRequest, CiMetadata, DeploymentStatus

app = FastAPI()
logger = logging.getLogger(__name__)
settings = Settings()


app.description = "Open api schema for CIR"
app.openapi_version = "3.0.1"
app.title = "Collection Instrumentation Register"
app.version = "1.0.0"


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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    When a request contains invalid data, FastAPI internally raises a `RequestValidationError`.
    This function override the default validation exception handler to return 400 instead of 422
    """
    # Build the error message as a semi-colon separated string of error messages
    message = ";".join([e["msg"] for e in exc.errors()])
    response_content = BadRequest(message=message)
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=asdict(response_content))


@app.delete(
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
async def http_delete_ci_v1(query_params: DeleteCiV1Params = Depends()):
    """
    DELETE method that deletes the CI schema from the bucket as well as the CI metadata from Firestore.
    """
    success_message = delete_ci_v1(query_params)

    if success_message:
        logger.info("delete_ci_v1 success")
        return JSONResponse(status_code=status.HTTP_200_OK, content=success_message)
    else:
        # Nothing to delete so return 404
        response_content = BadRequest(message=f"No CI found for: {asdict(query_params)}")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=asdict(response_content))


# Fetching CI Metadata from Firestore
@app.get(
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
async def http_get_ci_metadata_v1(query_params: GetCiMetadataV1Params = Depends()):
    """
    GET method that returns any metadata objects from Firestore that match the parameters passed.
    """
    ci_metadata = get_ci_metadata_v1(query_params)

    if ci_metadata:
        logger.info("get_ci_metadata_v1 success")
        return JSONResponse(status_code=status.HTTP_200_OK, content=ci_metadata)
    else:
        logger.info(
            f"get_ci_metadata_v1: exception raised - No CI(s) found for: {asdict(query_params)}",
        )
        response_content = BadRequest(message=f"No CI metadata found for: {asdict(query_params)}")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=asdict(response_content))


@app.get(
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
async def http_get_ci_metadata_v2(query_params: GetCiMetadataV2Params = Depends()):
    """
    GET method that returns any metadata objects from Firestore that match the parameters passed.
    The user has multiple ways of querying the metadata.
    1. Provide survey_id, form_type, language and status.
    2. Provide survey_id, form_type, language.
    3. Provide status.
    4. Provide no parameters.
    """
    ci_metadata = get_ci_metadata_v2(query_params)

    if ci_metadata:
        logger.info("get_ci_metadata_v2 success")
        return JSONResponse(status_code=status.HTTP_200_OK, content=ci_metadata)
    else:
        logger.info(
            f"get_ci_metadata_v2: exception raised - No CI(s) found for: {asdict(query_params)}",
        )
        response_content = BadRequest(message=f"No CI metadata found for: {asdict(query_params)}")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=asdict(response_content))


# Fetching CI schema from Bucket version 1
@app.get(
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
async def http_get_ci_schema_v1(query_params: GetCiSchemaV1Params = Depends()):
    """
    GET method that fetches a CI schema by it's survey_id, form_type and language.
    """
    ci_metadata_id, ci_schema = get_ci_schema_v1(query_params)

    if ci_metadata_id and ci_schema:
        logger.info("get_ci_metadata_v1 success")
        return JSONResponse(status_code=status.HTTP_200_OK, content=ci_schema)
    if not ci_metadata_id:
        message = f"No metadata found for: {asdict(query_params)}"
    else:
        message = f"No schema found for: {asdict(query_params)}"
    logger.info(
        f"get_ci_schema_v1: exception raised - {message}",
    )
    response_content = BadRequest(message=message)
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=asdict(response_content))


# Fetching CI schema from Bucket Version 2
@app.get(
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
async def http_get_ci_schema_v2(query_params: GetCiSchemaV2Params = Depends()):
    """
    GET method that fetches a CI schema by it's GUID.
    """
    ci_metadata, ci_schema = get_ci_schema_v2(query_params)

    if ci_metadata and ci_schema:
        logger.info("get_ci_metadata_v1 success")
        return JSONResponse(status_code=status.HTTP_200_OK, content=ci_schema)
    if not ci_metadata:
        message = f"No CI metadata found for: {query_params.guid}"
    else:
        message = f"No schema found for: {query_params.guid}"
    logger.info(
        f"get_ci_schema_v2: exception raised - {message}",
    )
    response_content = BadRequest(message=message)
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=asdict(response_content))


@app.post(
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
async def http_post_ci_metadata_v1(post_data: PostCiMetadataV1PostData):
    """
    POST method that creates a Collection Instrument. This will post the metadata to Firestore and
    the whole request body to a Google Cloud Bucket.
    """
    ci_metadata = post_ci_metadata_v1(post_data)
    logger.info("post_ci_metadata_v1 success")
    return JSONResponse(status_code=status.HTTP_200_OK, content=ci_metadata.model_dump())


@app.put(
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
async def http_put_status_v1(query_params: PutStatusV1Params = Depends()):
    """
    PUT method that sets the status of a CI's metadata in Firestore to 'PUBLISH'.
    """
    ci_metadata, updated_status = put_status_v1(query_params)
    if ci_metadata:
        if updated_status:
            message = f"CI status has been changed to Published for {query_params.guid}."
        else:
            logger.info("CI already set to PUBLISHED")
            message = f"CI status has already been changed to Published for {query_params.guid}."

        return JSONResponse(status_code=status.HTTP_200_OK, content=message)
    else:
        response_content = BadRequest(message=f"No CI metadata found for: {query_params.guid}")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=asdict(response_content))


@app.get(
    "/status",
    responses={
        status.HTTP_200_OK: {
            "model": DeploymentStatus,
            "description": ("Deployment done succuessfully"),
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": BadRequest,
            "description": "Internal error. This is triggered when something an unexpected error occurs on the server side.",
        },
    },
)
async def http_get_status():
    """
    GET method that returns `CIR_APPLICATION_VERSION` if the deployment is successful
    """
    application_version = settings.CIR_APPLICATION_VERSION
    if application_version:
        response_content = DeploymentStatus(version=settings.CIR_APPLICATION_VERSION)
        return JSONResponse(status_code=status.HTTP_200_OK, content=asdict(response_content))
    else:
        response_content = BadRequest(message="Internal server error")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=asdict(response_content))
