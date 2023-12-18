from dataclasses import asdict

from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import Settings

from app.models.responses import BadRequest, CiMetadata, DeploymentStatus

app = FastAPI()
settings = Settings()

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