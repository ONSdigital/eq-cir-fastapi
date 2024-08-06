import pytest

from app.models.requests import GetCiMetadataV2Params, PostCiSchemaV1Data

mock_classifier_type = "form_type"
mock_classifier_value = "0005"
mock_language = "en"
mock_survey_id = "123"
mock_description = "Version of CI is for March 2023 – APPROVED"


class TestGetCiMetadataV2Params:
    """Tests for the `GetCiMetadataV2Params` data class"""

    query_params = GetCiMetadataV2Params(
        classifier_type=mock_classifier_type,
        classifier_value=mock_classifier_value,
        language=mock_language,
        survey_id=mock_survey_id,
    )

    def test_params_not_none_returns_true_when_all_params_not_none(self):
        """`params_not_none` class method should return `True` if all param name strings as input
        arguments have a corresponding non-none class attribute value
        """
        assert self.query_params.params_not_none(self.query_params.__dict__.keys()) is True

    def test_params_all_none_returns_false_when_all_params_none(self):
        """`params_not_none` class method should return `False` if all param name strings as input
        arguments have a corresponding non-none class attribute value
        """
        assert self.query_params.params_all_none(self.query_params.__dict__.keys()) is False

    @pytest.mark.parametrize("input_param", ["classifier_type", "classifier_value", "language", "status", "survey_id"])
    def test_params_not_none_returns_false_when_single_param_none(self, input_param):
        """`params_not_none` class method should return `False` if any of param name strings as input
        arguments have a corresponding class attribute value of `None`
        """
        # Update `query_params` to contain a single `None` value
        setattr(self.query_params, input_param, None)

        assert self.query_params.params_not_none(self.query_params.__dict__.keys()) is False

    def test_params_not_none_returns_false_when_all_params_none(self):
        """`params_not_none` class method should return `False` if all param name strings as input
        arguments have a corresponding class attribute value of `None`
        """
        # Update `query_params` to contain `None` values
        self.query_params.classifier_value = None
        self.query_params.classifier_type = None
        self.query_params.language = None
        self.query_params.status = None
        self.query_params.survey_id = None

        assert self.query_params.params_not_none(self.query_params.__dict__.keys()) is False


class TestPostCiSchemaV1Data:
    """Tests for the `PostCiSchemaV1Data` Pydantic data model"""

    post_data = {
        "data_version": "1",
        "form_type": mock_classifier_value,
        "language": mock_language,
        "survey_id": mock_survey_id,
        "title": "test",
        "schema_version": "1",
        "description": mock_description,
    }

    def test_data_model_instantiates_with_valid_post_data(self):
        """`PostCiSchemaV1Data` data model should instantiate successfully if provided with the
        minimum valid input data
        """
        post_data_model = PostCiSchemaV1Data(**self.post_data)
        # Dictionary returned from data model should contain the original input data
        assert self.post_data.items() <= post_data_model.model_dump().items()

    @pytest.mark.parametrize(
        "input_param",
        [
            "data_version",
            "classifier_type",
            "classifier_value",
            "language",
            "survey_id",
            "title",
            "schema_version",
        ],
    )
    def test_data_model_raises_value_error_if_required_field_is_none(self, input_param):
        """`PostCiSchemaV1Data` data model should raise `ValueError` on init if any required
        field is `None`
        """
        # update `post_data` to contain `None` value for `input_param` field
        self.post_data.update({input_param: None})

        with pytest.raises(ValueError):
            PostCiSchemaV1Data(**self.post_data)

    @pytest.mark.parametrize(
        "input_param",
        [
            "data_version",
            "classifier_type",
            "classifier_value",
            "language",
            "survey_id",
            "title",
            "schema_version",
        ],
    )
    def test_data_model_raises_value_error_if_required_field_is_empty_string(self, input_param):
        """`PostCiSchemaV1Data` data model should raise `ValueError` on init if any required
        field is an empty string
        """
        # update `post_data` to contain an empty string value for `input_param` field
        self.post_data.update({input_param: ""})

        with pytest.raises(ValueError):
            PostCiSchemaV1Data(**self.post_data)

    @pytest.mark.parametrize(
        "input_param",
        [
            "data_version",
            "classifier_type",
            "classifier_value" "language",
            "survey_id",
            "title",
            "schema_version",
        ],
    )
    def test_data_model_raises_value_error_if_required_field_is_whitespace(self, input_param):
        """`PostCiSchemaV1Data` data model should raise `ValueError` on init if any required
        field is whitespace
        """
        # update `post_data` to contain a whitespace value for `input_param` field
        self.post_data.update({input_param: " "})

        with pytest.raises(ValueError):
            PostCiSchemaV1Data(**self.post_data)
