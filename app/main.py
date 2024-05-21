from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

import app.exception.exceptions as exceptions
from app.config import Settings, logging
from app.exception.exception_interceptor import ExceptionInterceptor
from app.routers import ci_router, status_router

app = FastAPI()
logger = logging.getLogger(__name__)
settings = Settings()


app.description = "Open api schema for CIR"
app.openapi_version = "3.0.1"
app.title = "Collection Instrumentation Register"
app.version = "1.0.0"


app.add_exception_handler(
    exceptions.ExceptionNoCIMetadata,
    ExceptionInterceptor.throw_404_no_ci_metadata_exception,
)
app.add_exception_handler(
    exceptions.ExceptionNoCIFound,
    ExceptionInterceptor.throw_404_no_ci_to_delete,
)
app.add_exception_handler(
    exceptions.ExceptionNoCIFound,
    ExceptionInterceptor.throw_404_no_ci_exception,
)
app.add_exception_handler(
    exceptions.ExceptionIncorrectKeyNames,
    ExceptionInterceptor.throw_400_incorrect_key_names_exception,
)
app.add_exception_handler(
    exceptions.GlobalException,
    ExceptionInterceptor.throw_500_global_exception,
)
app.add_exception_handler(
    exceptions.ValidationException,
    ExceptionInterceptor.throw_400_validation_exception,
)


@app.exception_handler(500)
async def internal_exception_handler(request: Request, exc: Exception):
    """
    Override the global exception handler (500 internal server error) in
    FastAPI and throw error in JSON format
    """
    return ExceptionInterceptor.throw_500_global_exception(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    When a request contains invalid data, FastAPI internally raises a
    RequestValidationError. This function override the default
    validation exception handler to return 400 instead of 422
    """
    return ExceptionInterceptor.throw_400_validation_exception(request, exc)


app.include_router(ci_router.router)
app.include_router(status_router.router)
