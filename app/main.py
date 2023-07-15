from fastapi import Depends, FastAPI, Response, status

from app.config import logging, Settings
from app.handlers import get_ci_metadata_v1
from app.models.requests import GetCiMetadataParams
from app.models.responses import bad_request

app = FastAPI()
logger = logging.getLogger(__name__)
settings = Settings()


@app.get("/")
async def read_root():
    return settings.model_dump()


@app.get("/v1/ci_metadata")
async def http_get_ci_metadata_v1(response: Response, query_params: GetCiMetadataParams = Depends()):
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
            f"get_ci_metadata_v1: exception raised - No CI(s) found for: {query_params.model_dump()}",
        )
        return bad_request(f"No CI metadata found for: {query_params.model_dump()}")
