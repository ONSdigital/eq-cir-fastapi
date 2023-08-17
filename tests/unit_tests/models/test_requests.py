import pytest

from app.models.requests import GetCiMetadataV2Params, PostCiMetadataV1PostData
from app.models.responses import CiStatus

mock_form_type = "0005"
mock_language = "en"
mock_status = CiStatus.DRAFT.value
mock_survey_id = "123"
mock_description = "Version of CI is for March 2023 – APPROVED"


class TestGetCiMetadataV2Params:
    """Tests for the `GetCiMetadataV2Params` data class"""

    query_params = GetCiMetadataV2Params(
        form_type=mock_form_type, language=mock_language, status=mock_status, survey_id=mock_survey_id
    )

    def test_params_not_none_returns_true_when_all_params_not_none(self):
        """
        `params_not_none` class method should return `True` if all param name strings as input
        arguments have a corresponding non-none class attribute value
        """
        assert self.query_params.params_not_none("form_type", "language", "status", "survey_id") is True

    @pytest.mark.parametrize("input_param", ["form_type", "language", "status", "survey_id"])
    def test_params_not_none_returns_false_when_single_param_none(self, input_param):
        """
        `params_not_none` class method should return `False` if any of param name strings as input
        arguments have a corresponding class attribute value of `None`
        """
        # Update `query_params` to contain a single `None` value
        setattr(self.query_params, input_param, None)

        assert self.query_params.params_not_none("form_type", "language", "status", "survey_id") is False

    def test_params_not_none_returns_false_when_all_params_none(self):
        """
        `params_not_none` class method should return `False` if all param name strings as input
        arguments have a corresponding class attribute value of `None`
        """
        # Update `query_params` to contain `None` values
        self.query_params.form_type = None
        self.query_params.language = None
        self.query_params.status = None
        self.query_params.survey_id = None

        assert self.query_params.params_not_none("form_type", "language", "status", "survey_id") is False


class TestPostCiMetadataV1PostData:
    """Tests for the `PostCiMetadataV1PostData` Pydantic data model"""

    post_data = {
        "data_version": "1",
        "form_type": mock_form_type,
        "language": mock_language,
        "survey_id": mock_survey_id,
        "title": "test",
        "schema_version": "1",
        "description": mock_description,
    }

    def test_data_model_instantiates_with_valid_post_data(self):
        """
        `PostCiMetadataV1PostData` data model should instantiate successfully if provided with the
        minimum valid input data
        """
        post_data_model = PostCiMetadataV1PostData(**self.post_data)
        # Dictionary returned from data model should contain the original input data
        assert self.post_data.items() <= post_data_model.model_dump().items()

    @pytest.mark.parametrize("input_param", ["data_version", "form_type", "language", "survey_id", "title", "schema_version"])
    def test_data_model_raises_value_error_if_required_field_is_none(self, input_param):
        """
        `PostCiMetadataV1PostData` data model should raise `ValueError` on init if any required
        field is `None`
        """
        # update `post_data` to contain `None` value for `input_param` field
        self.post_data.update({input_param: None})

        with pytest.raises(ValueError):
            PostCiMetadataV1PostData(**self.post_data)

    @pytest.mark.parametrize("input_param", ["data_version", "form_type", "language", "survey_id", "title", "schema_version"])
    def test_data_model_raises_value_error_if_required_field_is_empty_string(self, input_param):
        """
        `PostCiMetadataV1PostData` data model should raise `ValueError` on init if any required
        field is an empty string
        """
        # update `post_data` to contain an empty string value for `input_param` field
        self.post_data.update({input_param: ""})

        with pytest.raises(ValueError):
            PostCiMetadataV1PostData(**self.post_data)

    @pytest.mark.parametrize("input_param", ["data_version", "form_type", "language", "survey_id", "title", "schema_version"])
    def test_data_model_raises_value_error_if_required_field_is_whitespace(self, input_param):
        """
        `PostCiMetadataV1PostData` data model should raise `ValueError` on init if any required
        field is whitespace
        """
        # update `post_data` to contain a whitespace value for `input_param` field
        self.post_data.update({input_param: " "})

        with pytest.raises(ValueError):
            PostCiMetadataV1PostData(**self.post_data)
