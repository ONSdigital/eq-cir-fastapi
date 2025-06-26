from fastapi import Request, status
from fastapi.responses import JSONResponse

import app.exception.exception_response_models as erm
from app.exception.exception_responder import ExceptionResponder


class ExceptionInterceptor:
    def throw_500_global_exception(request: Request, exc: Exception) -> JSONResponse:
        """
        When an exception is raised and a global error 500 HTTP response is returned.
        """
        er = ExceptionResponder(status.HTTP_500_INTERNAL_SERVER_ERROR, erm.erm_500_global_exception)
        return er.throw_er_with_json()

    def throw_400_validation_exception(request: Request, exc: Exception) -> JSONResponse:
        """
        When a validation fails and a 400 HTTP response is returned.
        """
        er = ExceptionResponder(status.HTTP_400_BAD_REQUEST, erm.erm_400_validation_exception)
        return er.throw_er_with_json()

    def throw_404_no_ci_metadata_exception(request: Request, exc: Exception) -> JSONResponse:
        """
        When there is no schema metadata and a 404 HTTP response is returned.
        """
        er = ExceptionResponder(status.HTTP_404_NOT_FOUND, erm.erm_404_no_results_exception)
        return er.throw_er_with_json()

    def throw_400_no_validator_provided_exception(request: Request, exc: Exception) -> JSONResponse:
        """
        When there is no schema metadata and a 404 HTTP response is returned.
        """
        er = ExceptionResponder(status.HTTP_400_BAD_REQUEST, erm.erm_404_no_validator_version_exception)
        return er.throw_er_with_json()

    def throw_404_no_ci_to_delete(request: Request, exc: Exception) -> JSONResponse:
        """
        When there is No CI found and a 404 HTTP response is returned
        Triggered when either schema metadata or schema json file is not found
        """
        er = ExceptionResponder(status.HTTP_404_NOT_FOUND, erm.erm_404_no_ci_to_delete)
        return er.throw_er_with_json()

    def throw_404_no_ci_exception(request: Request, exc: Exception) -> JSONResponse:
        """
        When there is No CI found and a 404 HTTP response is returned
        Triggered when either schema metadata or schema json file is not found
        """
        er = ExceptionResponder(status.HTTP_404_NOT_FOUND, erm.erm_404_no_ci_exception)
        return er.throw_er_with_json()

    def throw_400_invalid_clasifier_exception(request: Request, exc: Exception) -> JSONResponse:
        """
        When there is No CI found and a 404 HTTP response is returned
        Triggered when either schema metadata or schema json file is not found
        """
        er = ExceptionResponder(status.HTTP_400_BAD_REQUEST, erm.erm_400_invalid_classifier)
        return er.throw_er_with_json()

    def throw_400_incorrect_key_names_exception(request: Request, exc: Exception) -> JSONResponse:
        """
        When there is No CI found and a 404 HTTP response is returned
        Triggered when either schema metadata or schema json file is not found
        """
        er = ExceptionResponder(status.HTTP_400_BAD_REQUEST, erm.erm_400_incorrect_key_names_exception)
        return er.throw_er_with_json()


exception_interceptor = ExceptionInterceptor()
