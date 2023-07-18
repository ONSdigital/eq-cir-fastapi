from fastapi import Depends, FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import Settings, logging
from app.handlers import get_ci_metadata_v1
from app.models.requests import GetCiMetadataV1Params
from app.models.responses import BadRequest, CiMetadata

app = FastAPI()
logger = logging.getLogger(__name__)
settings = Settings()


app.description = "Open api schema for CIR"
# app.openapi_version = "2.0.0"
app.title = "Collection Instrumentation Register"
app.version = "1.0.0"


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
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
        return JSONResponse(status_code=status.HTTP_200_OK, content={})
    else:
        logger.info(
            f"get_ci_metadata_v1: exception raised - No CI(s) found for: {query_params.__dict__}",
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": f"No CI metadata found for: {query_params.__dict__}"}
        )
