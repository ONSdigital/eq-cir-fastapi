from unittest.mock import patch

from app.handlers import get_ci_metadata_v1, delete_ci_v1
from app.models.requests import GetCiMetadataV1Params, DeleteCiV1Params


@patch("app.handlers.query_ci_metadata")
class TestGetCiMetadataV1:
    """Tests for the `get_ci_metadata_v1` handler"""

    mock_form_type = "t"
    mock_language = "em"
    mock_survey_id = "12124141"

    mock_ci_metadata = {
        "data_version": "1",
        "form_type": mock_form_type,
        "language": mock_language,
        "schema_version": "12",
        "survey_id": mock_survey_id,
        "title": "test",
    }

    query_params = GetCiMetadataV1Params(form_type=mock_form_type, language=mock_language, survey_id=mock_survey_id)

    def test_handler_calls_query_ci_metadata(self, mocked_query_ci_metadata):
        """
        `get_ci_metadata_v1` should call `query_ci_metadata` to query the database for ci metadata
        """
        get_ci_metadata_v1(self.query_params)
        mocked_query_ci_metadata.assert_called_once()

    def test_handler_calls_query_ci_metadata_with_correct_inputs(self, mocked_query_ci_metadata):
        """
        `get_ci_metadata_v1` should call `query_ci_metadata` to query the database for ci metadata
        `query_ci_metadata` should be called with the correct, `form_type`, `language` and
        `survey_id` inputs
        """
        get_ci_metadata_v1(self.query_params)
        mocked_query_ci_metadata.assert_called_with(self.mock_survey_id, self.mock_form_type, self.mock_language)

    def test_handler_returns_output_of_query_ci_metadata(self, mocked_query_ci_metadata):
        """
        `get_ci_metadata_v1` should return the output of `query_ci_metadata`
        """
        # Update mocked `query_ci_metadata` to return valid ci metadata
        mocked_query_ci_metadata.return_value = self.mock_ci_metadata
        response = get_ci_metadata_v1(self.query_params)

        assert response == self.mock_ci_metadata


#@patch("app.handlers.delete_ci_v1")
class TestHttpDeleteCiV1:

    mock_form_type = "t"
    mock_language = "em"
    mock_survey_id = "12124141"

    mock_ci_metadata = {
        "data_version": "1",
        "form_type": mock_form_type,
        "language": mock_language,
        "schema_version": "12",
        "survey_id": mock_survey_id,
        "title": "test",
    }

    query_params = DeleteCiV1Params(survey_id=mock_survey_id)

    @patch("app.handlers.query_ci_by_survey_id")
    def test_handler_calls_query_ci_by_survey_id_(self, mocked_delete_ci_metadata):
        """
        `delete_ci_metadata_v1` should call `query_ci_bu survey`
        """

        delete_ci_v1(self.query_params)
        mocked_delete_ci_metadata.assert_called_once(self.mock_survey_id)

    @patch("app.handlers.query_ci_by_survey_id")
    def test_handler_calls_query_ci_by_survey_id_with_correct_inputs(self, mocked_delete_ci_metadata):
        """
        `delete_ci_metadata_v1` should call `query_ci_bu survey`
        """

        delete_ci_v1(self.query_params)
        mocked_delete_ci_metadata.assert_called_with(self.mock_survey_id)

    @patch("app.handlers.delete_ci_metadata")
    def test_handler_calls_delete_ci_metadata(self, mocked_query_ci_metadata):
        """
        `get_ci_metadata_v1` should call `query_ci_metadata` to query the database for ci metadata
        """
        delete_ci_v1(self.query_params)
        mocked_query_ci_metadata.assert_called_once()

    @patch("app.handlers.delete_ci_metadata")
    def test_handler_calls_delete_ci_metadata_with_correct_inputs(self, mocked_delete_ci_metadata):
        """
           `delete_ci_metadata_v1` should call `delete ci metadata'
        """
        delete_ci_v1(self.query_params)
        mocked_delete_ci_metadata.assert_called_with(self.mock_survey_id)

    @patch("app.handlers.delete_ci_schema")
    def test_handler_calls_delete_ci_schema(self, mocked_delete_ci_schema):
        """
        `get_ci_metadata_v1` should call `query_ci_metadata` to query the database for ci metadata
        """
        delete_ci_v1(self.query_params)
        mocked_delete_ci_schema.assert_called_once()

    @patch("app.handlers.delete_ci_schema")
    def test_handler_calls_delete_ci_schema_with_correct_inputs(self, mocked_delete_ci_schema):
        """
        `delete_ci_schema_v1` should call `delete ci schema'
        """
        delete_ci_v1(self.query_params)
        mocked_delete_ci_schema.assert_called_with(self.mock_survey_id)








