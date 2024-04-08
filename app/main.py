from dataclasses import asdict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import Settings, logging
from app.models.responses import BadRequest
from app.routers import ci_router, status_router

app = FastAPI()
logger = logging.getLogger(__name__)
settings = Settings()


app.description = "Open api schema for CIR"
app.openapi_version = "3.0.1"
app.title = "Collection Instrumentation Register"
app.version = "1.0.0"

app.include_router(ci_router.router)
app.include_router(status_router.router)


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