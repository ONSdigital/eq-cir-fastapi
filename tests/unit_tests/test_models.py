from app.models.requests import GetCiMetadataV2Params


class TestGetCiMetadataV2Params:
    """Tests for the `GetCiMetadataV2Params` data class"""

    query_params = GetCiMetadataV2Params(form_type="0005", language="en", status="draft", survey_id="123")

    def test_params_not_none_returns_true_when_all_params_not_none(self):
        """
        `params_not_none` class method should return `True` if all param name strings as input
        arguments have a corresponding non-none class attribute value
        """
        assert self.query_params.params_not_none("form_type", "language", "status", "survey_id") == True

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

        assert self.query_params.params_not_none("form_type", "language", "status", "survey_id") == False

    def test_params_not_none_returns_false_when_single_param_none(self):
        """
        `params_not_none` class method should return `False` if al param name strings as input
        arguments have a corresponding class attribute value of `None`
        """
        pass