from exception.exception_response_models import ExceptionResponseModel
from fastapi.responses import JSONResponse


class ExceptionResponder:
    status_code: int
    response: ExceptionResponseModel

    def __init__(self, status_code: int, response: ExceptionResponseModel) -> None:
        self.status_code = status_code
        self.response = response

    def throw_er_with_json(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status_code,
            content=self.response.__dict__,
        )
