from pydantic import BaseModel


class ExceptionResponseModel(BaseModel):
    status: str
    message: str


erm_500_global_exception = ExceptionResponseModel(status="error", message="Unable to process request")
erm_400_validation_exception = ExceptionResponseModel(status="error", message="Validation has failed")
erm_400_incorrect_key_names_exception = ExceptionResponseModel(status="error", message="Invalid search parameters provided")
erm_404_no_results_exception = ExceptionResponseModel(status="error", message="No results found")
erm_404_no_validator_version_exception = ExceptionResponseModel(status="error", message="No validator version provided")
erm_404_no_ci_exception = ExceptionResponseModel(status="error", message="No CI found")
erm_400_invalid_classifier = ExceptionResponseModel(status="error", message="Invalid classifier")
erm_404_no_ci_metadata_exception = ExceptionResponseModel(status="error", message="No schema metadata to update")
erm_404_no_ci_to_delete = ExceptionResponseModel(status="error", message="No CI to delete")
