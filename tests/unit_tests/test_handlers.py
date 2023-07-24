from unittest.mock import patch

from app.handlers import get_ci_metadata_v1, get_ci_schema_v1, get_ci_schema_v2
from app.models.requests import (
    GetCiMetadataV1Params,
    GetCiSchemaV1Params,
    GetCiSchemaV2Params,
)


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


@patch("app.handlers.retrieve_ci_schema")
@patch("app.handlers.query_latest_ci_version_id")
class TestGetCISchemaV1:
    """Tests for the `get_ci_metadata_v1` handler"""

    mock_form_type = "t"
    mock_language = "em"
    mock_survey_id = "12124141"
    mock_id = "123578"

    mock_ci_schema = {
        "data_version": "1",
        "form_type": mock_form_type,
        "language": mock_language,
        "schema_version": "12",
        "survey_id": mock_survey_id,
        "title": "test",
    }

    query_params = GetCiSchemaV1Params(form_type=mock_form_type, language=mock_language, survey_id=mock_survey_id)

    def test_handler_calls_retrive_ci_schema(self, mocked_query_ci_schema, mocked_query_latest_ci_version_id):
        """
        `get_ci_schema_v1` should call `query_ci_metadata` to query the database for ci metadata
        """

        get_ci_schema_v1(self.query_params)
        mocked_query_ci_schema.assert_called_once()
        mocked_query_latest_ci_version_id.assert_called_once()

    def test_handler_calls_retrive_ci_schema_with_correct_inputs(
        self, mocked_query_ci_schema, mocked_query_latest_ci_version_id
    ):
        """
        `get_ci_schema_v1`` should call `retrieve_ci_schema` to retrive the schema
        `retrive_ci_schema` should be called with the correct, `form_type`, `language` and
        `survey_id` inputs
        """

        get_ci_schema_v1(self.query_params)
        mocked_query_ci_schema.assert_called_with(self.mock_survey_id, self.mock_form_type, self.mock_language)

    def test_handler_returns_output_of_retrive_ci_schema(self, mocked_query_ci_schema, mocked_query_latest_ci_version_id):
        """
        `get_ci_schema_v1` should return the output of `query_ci_metadata`
        """
        # Update mocked `query_ci_metadata` to return valid ci metadata
        mocked_query_latest_ci_version_id.return_value = "123578"
        mocked_query_ci_schema.return_value = self.mock_ci_schema
        response, metadata_id = get_ci_schema_v1(self.query_params)
        assert response == self.mock_ci_schema
        assert metadata_id == "123578"


@patch("app.handlers.retrieve_ci_schema")
@patch("app.handlers.query_ci_metadata_with_guid")
class TestGetCISchemaV2:
    """Tests for the `get_ci_schema_v1` handler"""

    mock_form_type = "t"
    mock_language = "em"
    mock_survey_id = "12124141"
    mock_id = "123578"

    mock_ci_schema = {
        "data_version": "1",
        "form_type": mock_form_type,
        "language": mock_language,
        "schema_version": "12",
        "survey_id": mock_survey_id,
        "title": "test",
    }

    query_params = GetCiSchemaV2Params(id=mock_id)

    def test_handler_calls_retrive_ci_schema(self, mocked_query_ci_schema, mocked_query_ci_metadata_with_guid):
        """
        `get_ci_schema_v2` should call `retrive_ci_schema` to query the database for ci metadata
        """

        get_ci_schema_v2(self.query_params)
        mocked_query_ci_schema.assert_called_once()
        mocked_query_ci_metadata_with_guid.assert_called_once()

    def test_handler_calls_retrive_ci_schema_with_correct_inputs(
        self, mocked_query_ci_schema, mocked_query_ci_metadata_with_guid
    ):
        """
        `get_ci_metadata_v2` should call `retrive_ci_schema` to query the database for ci metadata
        `retrive_ci_schema` should be called with the correct, `id` inputs
        """

        get_ci_schema_v2(self.query_params)
        mocked_query_ci_schema.assert_called_with(self.mock_id)

    def test_handler_returns_output_of_retrive_ci_schema(self, mocked_query_ci_schema, mocked_query_ci_metadata_with_guid):
        """
        `get_ci_schema_v2` should return the output of `retrive_ci_schema`
        """
        # Update mocked `query_ci_metadata` to return valid ci metadata
        mocked_query_ci_metadata_with_guid.return_value = self.mock_ci_schema
        mocked_query_ci_schema.return_value = self.mock_ci_schema
        metadata, schema = get_ci_schema_v2(self.query_params)
        assert metadata == self.mock_ci_schema
        assert schema == self.mock_ci_schema
