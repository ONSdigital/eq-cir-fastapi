import exception.exception_response_models as erm
from exception.exception_responder import ExceptionResponder
from fastapi import Request, status
from fastapi.responses import JSONResponse


class ExceptionInterceptor:
    def throw_500_global_exception(request: Request, exc: Exception) -> JSONResponse:
        """
        When an exception is raised and a global error 500 HTTP response is returned.
        """
        er = ExceptionResponder(
            status.HTTP_500_INTERNAL_SERVER_ERROR, erm.erm_500_global_exception
        )
        return er.throw_er_with_json()

    def throw_400_validation_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        When a validation fails and a 400 HTTP response is returned.
        """
        er = ExceptionResponder(
            status.HTTP_400_BAD_REQUEST, erm.erm_400_validation_exception
        )
        return er.throw_er_with_json()

    def throw_400_incorrect_schema_key_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        When wrong search parameters are supplied for schema or schema metadata query and a 400 HTTP response is returned.
        """
        er = ExceptionResponder(
            status.HTTP_400_BAD_REQUEST, erm.erm_400_invalid_search_exception
        )
        return er.throw_er_with_json()

    def throw_400_incorrect_schema_v2_key_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        When wrong search parameters are supplied for schema v2 query and a 400 HTTP response is returned.
        """
        er = ExceptionResponder(
            status.HTTP_400_BAD_REQUEST, erm.erm_400_invalid_parameter_exception
        )
        return er.throw_er_with_json()

    def throw_404_no_schemas_metadata_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        When there is no schema metadata and a 404 HTTP response is returned.
        """
        er = ExceptionResponder(
            status.HTTP_404_NOT_FOUND, erm.erm_404_no_results_exception
        )
        return er.throw_er_with_json()

    def throw_404_no_schema_exception(request: Request, exc: Exception) -> JSONResponse:
        """
        When there is no schema found and a 404 HTTP response is returned
        Triggered when either schema metadata or schema json file is not found
        """
        er = ExceptionResponder(
            status.HTTP_404_NOT_FOUND, erm.erm_404_no_schema_exception
        )
        return er.throw_er_with_json()

    def throw_400_incorrect_key_names_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        When searching for the dataset metadata endpoint with the incorrect search
        queries a 400 HTTP response is returned
        """
        er = ExceptionResponder(
            status.HTTP_400_BAD_REQUEST, erm.erm_400_incorrect_key_names_exception
        )
        return er.throw_er_with_json()

    def throw_404_no_result_exception(request: Request, exc: Exception) -> JSONResponse:
        """
        When there is no dataset metadata endpoint and a 404 HTTP response is returned
        """
        er = ExceptionResponder(
            status.HTTP_404_NOT_FOUND, erm.erm_404_no_datasets_exception
        )
        return er.throw_er_with_json()

    def throw_404_unit_data_no_response_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Querying the dataset unit data with no result found triggers a 404
        HTTP response
        """
        er = ExceptionResponder(
            status.HTTP_404_NOT_FOUND, erm.erm_404_no_unit_data_exception
        )
        return er.throw_er_with_json()

    def throw_404_no_survey_id_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        When there are no survey IDs and a 404 HTTP response is returned
        """
        er = ExceptionResponder(
            status.HTTP_404_NOT_FOUND, erm.erm_404_no_survey_id_exception
        )
        return er.throw_er_with_json()


exception_interceptor = ExceptionInterceptor()
