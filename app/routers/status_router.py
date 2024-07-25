from dataclasses import asdict

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

import app.exception.exception_response_models as erm
from app.config import Settings
from app.exception import exceptions
from app.exception.exception_response_models import ExceptionResponseModel
from app.models.responses import DeploymentStatus

router = APIRouter()
settings = Settings()


@router.get(
    "/status",
    responses={
        status.HTTP_200_OK: {
            "model": DeploymentStatus,
            "description": "Deployment done successfully",
        },
        500: {
            "model": ExceptionResponseModel,
            "content": {"application/json": {"example": erm.erm_500_global_exception}},
        },
    },
)
async def http_get_status():
    """GET method that returns `CIR_APPLICATION_VERSION` if the deployment is successful
    """
    application_version = settings.CIR_APPLICATION_VERSION
    if application_version:
        response_content = DeploymentStatus(version=settings.CIR_APPLICATION_VERSION)
        return JSONResponse(status_code=status.HTTP_200_OK, content=asdict(response_content))
    else:
        raise exceptions.GlobalException
