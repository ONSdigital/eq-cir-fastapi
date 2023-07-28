from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.config import Settings, logging
from app.handlers import get_ci_metadata_v1, delete_ci_v1, get_ci_metadata_v2, post_ci_metadata_v1
from app.models.requests import GetCiMetadataV1Params, PostCiMetadataV1Params, DeleteCiV1Params, GetCiMetadataV2Params
from app.models.responses import BadRequest, CiMetadata

app = FastAPI()
logger = logging.getLogger(__name__)
settings = Settings()


app.description = "Open api schema for CIR"
# app.openapi_version = "2.0.0"
app.title = "Collection Instrumentation Register"
app.version = "1.0.0"


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    When a request contains invalid data, FastAPI internally raises a
    RequestValidationError. This function override the default
    validation exception handler to return 400 instead of 422
    """
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(exc)})


@app.get(
    "/v1/ci_metadata",
    responses={
        status.HTTP_200_OK: {
            "model": CiMetadata,
            "description": (
                "Successfully fetched the metadata of a CI. This is illustrated with the returned response containing the "
                "metadata of the CI."
            ),
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequest,
            "description": (
                "Bad request. This is triggered by when a bad request body is provided. The response will inform the user "
                "what required parameter they are missing from the request."
            ),
        },
        status.HTTP_404_NOT_FOUND: {
            "model": BadRequest,
            "description": "Bad request. This is triggered when there is no CI data that matches the request provided.",
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
            f"get_ci_metadata_v1: exception raised - No CI(s) found for: {query_params.__dict__}",
        )
        response_content = BadRequest(message=f"No CI metadata found for: {query_params.__dict__}")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=response_content.__dict__)


@app.get(
    "/v2/ci_metadata",
    responses={
        status.HTTP_200_OK: {
            "model": CiMetadata,
            "description": (
                "Successfully fetched the metadata of a CI. "
                "This is illustrated with the returned response containing the metadata of the CI."
            ),
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequest,
            "description": (
                "Bad request. This is triggered by when a bad request body is provided. "
                "The response will inform the user what required parameter they are missing from the request. "
                "what required parameter they are missing from the request."
            ),
        },
        status.HTTP_404_NOT_FOUND: {
            "model": BadRequest,
            "description": "Bad request. This is triggered when there is no CI data that matches the request provided.",
        },
    },
)
async def http_get_ci_metadata_v2(query_params: GetCiMetadataV2Params = Depends()):
    """
    GET method that returns any metadata objects from Firestore that match the parameters passed.
    The user has multiple ways of querying the metadata. 1. Provide survey_id, form_type, language and status. 2.
    Provide survey_id, form_type, language. 3. Provide status. 4. Provide no parameters.
    """
    ci_metadata = get_ci_metadata_v2(query_params)

    if ci_metadata:
        logger.info("get_ci_metadata_v1 success")
        return JSONResponse(status_code=status.HTTP_200_OK, content=ci_metadata)
    else:
        logger.info(
            f"get_ci_metadata_v1: exception raised - No CI(s) found for: {query_params.__dict__}",
        )
        response_content = BadRequest(message=f"No CI metadata found for: {query_params.__dict__}")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=response_content.__dict__)


@app.post(
    "/v1/publish_collection_instrument",
    responses={
        status.HTTP_200_OK: {
            "model": CiMetadata,
            "description": (
                "Successfully created a CI. This is illustrated with the returned response containing the metadata of the CI."
            ),
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequest,
            "description": (
                "Bad request. This is triggered by when a bad request body is provided. The response will inform the user "
                "what required parameter they are missing from the request or what is incorrect with the "
                "value that they have provided"
            ),
        },
        status.HTTP_404_NOT_FOUND: {
            "model": BadRequest,
            "description": "Internal error. This is triggered when something an unexpected error occurs on the server side.",
        },
    },
)
async def http_post_ci_metadata_v1(query_params: PostCiMetadataV1Params = Depends()):
    """
    GET method that returns any metadata objects from Firestore that match the parameters passed.
    """
    ci_metadata = post_ci_metadata_v1(query_params)

    if ci_metadata:
        logger.info("post_ci_metadata_v1 success")
        return JSONResponse(status_code=status.HTTP_200_OK, content=ci_metadata)
    else:
        logger.info(
            f"post_ci_metadata_v1: exception raised - No CI(s) found for: {query_params.__dict__}",
        )
        response_content = BadRequest(message=f"No CI metadata found for: {query_params.__dict__}")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=response_content.__dict__)


@app.delete(
    "/v1/dev/teardown",
    responses={
        status.HTTP_200_OK: {
            "model": CiMetadata,
            "description": (
                "Successfully fetched the metadata of a CI. This is illustrated with the returned response containing the "
                "metadata of the CI."
            ),
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BadRequest,
            "description": (
                "Bad request. This is triggered by when a bad request body is provided. The response will inform the user "
                "Bad request. This is triggered by when a bad request body is provided. "
                "The response will inform the user what required parameter they are missing from the request. "
                "what required parameter they are missing from the request."
            ),
        },
        status.HTTP_404_NOT_FOUND: {
            "model": BadRequest,
            "description": "Bad request. This is triggered when there is no CI data that matches the request provided.",
        },
    },
)
async def http_delete_ci_v1(query_params: DeleteCiV1Params = Depends()):
    """
    Delete method that returns any metadata objects from Firestore that match the parameters passed.
    """
    ci_metadata = delete_ci_v1(query_params)

    if ci_metadata:
        logger.info("delete_ci_v1 success")
        return JSONResponse(status_code=status.HTTP_200_OK, content=ci_metadata)
    else:
        logger.info(
            f"delete_ci_v1: exception raised - No CI(s) found for: {query_params.__dict__}",
        )
        return BadRequest(message=f"No CI found for: {query_params.__dict__}")
