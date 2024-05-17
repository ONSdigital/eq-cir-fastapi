from pydantic import BaseModel


class ExceptionResponseModel(BaseModel):
    status: str
    message: str


erm_500_global_exception = ExceptionResponseModel(status="error", message="Unable to process request")
erm_400_validation_exception = ExceptionResponseModel(status="error", message="Validation has failed")
erm_400_invalid_search_exception = ExceptionResponseModel(status="error", message="Invalid search provided")
erm_400_invalid_parameter_exception = ExceptionResponseModel(status="error", message="Invalid parameter provided")
erm_400_incorrect_key_names_exception = ExceptionResponseModel(status="error", message="Invalid search parameters provided")
erm_404_no_results_exception = ExceptionResponseModel(status="error", message="No results found")
erm_404_no_ci_exception = ExceptionResponseModel(status="error", message="No CI found")
erm_404_no_survey_id_exception = ExceptionResponseModel(status="error", message="No Survey IDs found")
