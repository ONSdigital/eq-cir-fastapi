from fastapi import Depends, FastAPI, Response, status

from app.config import Settings, logging
from app.handlers import get_ci_metadata_v1, get_ci_schema_v1
from app.models.requests import GetCiMetadataV1Params, GetCiSchemaV1Params
from app.models.responses import bad_request

app = FastAPI()
logger = logging.getLogger(__name__)
settings = Settings()


app.description = "Open api schema for CIR"
# app.openapi_version = "2.0.0"
app.title = "Collection Instrumentation Register"
app.version = "1.0.0"


@app.get("/v1/ci_metadata")
async def http_get_ci_metadata_v1(response: Response, query_params: GetCiMetadataV1Params = Depends()):
    """
    GET method that returns any metadata objects from Firestore that match the parameters passed.
    """
    ci_metadata = get_ci_metadata_v1(query_params)

    if ci_metadata:
        response.status_code = status.HTTP_200_OK
        logger.info("get_ci_metadata_v1 success")
        return ci_metadata
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        logger.info(
            f"get_ci_metadata_v1: exception raised - No CI(s) found for: {query_params.__dict__}",
        )
        return bad_request(f"No CI metadata found for: {query_params.__dict__}")


@app.get("/v1/retrieve_collection_instrument")
async def http_get_ci_schema_v1(response: Response, query_params: GetCiSchemaV1Params = Depends()):
    """
    GET method that returns any metadata objects from Firestore that match the parameters passed.
    """
    ci_metadata_id, ci_schema = get_ci_schema_v1(query_params)

    if ci_metadata_id and ci_schema:
        response.status_code = status.HTTP_200_OK
        logger.info("get_ci_schema_v1 success")
        return ci_schema
    if not ci_metadata_id:
        message = f"No metadata found for: {query_params.__dict__}"
    else:
        message = f"No schema found for: {query_params.__dict__}"
    response.status_code = status.HTTP_404_NOT_FOUND
    logger.info(
        f"get_ci_schema_v1: exception raised - {message}",
    )
    return bad_request(message)
