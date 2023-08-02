from unittest.mock import patch

from app.handlers import (
    get_ci_metadata_v1,
    get_ci_metadata_v2,
    get_ci_schema_v1,
    get_ci_schema_v2,
    put_status_v1,
)
from app.models.requests import (
    GetCiMetadataV1Params,
    GetCiMetadataV2Params,
    GetCiSchemaV1Params,
    GetCiSchemaV2Params,
    PutStatusV2Params,
    Status,
)


@patch("app.handlers.query_ci_metadata")
class TestGetCiMetadataV1:
    """
    Tests for the `get_ci_metadata_v1` handler

    All calls to `app.repositories.firestore.query_ci_metadata` are mocked out for these tests
    """

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


class TestGetCiMetadataV2:
    """Tests for the `get_ci_metadata_v2` handler"""

    mock_survey_id = "12124141"
    mock_language = "em"
    mock_form_type = "t"
    mock_title = "test"
    mock_schema_version = "12"
    mock_data_version = "1"
    mock_status = "DRAFT"

    mock_ci_list = [
        {
            "survey_id": mock_survey_id,
            "form_type": mock_form_type,
            "language": mock_language,
            "title": "test1",
            "ci_version": 1,
        },
        {
            "survey_id": mock_survey_id,
            "form_type": mock_form_type,
            "language": mock_language,
            "title": "test2",
            "ci_version": 2,
        },
    ]

    # Create a default, empty request (all params set to `None`)
    query_params = GetCiMetadataV2Params(form_type=None, language=None, status=None, survey_id=None)  # type: ignore [arg-type]

    @patch("app.handlers.get_all_ci_metadata")
    def test_get_ci_metadata_v2_with_no_parameters_returns_all_ci(self, mocked_get_all_ci_metadata):
        """
        Why am I testing:
            To check that all the CIs are returned when no parameters are supplied.
        What am I testing:
            Data containing multiple CI is returned when no params are passed
        """
        # Update mocked `get_all_ci_metadata` call to return list of valid ci
        mocked_get_all_ci_metadata.return_value = self.mock_ci_list

        items = get_ci_metadata_v2(self.query_params)
        assert items == self.mock_ci_list

    @patch("app.handlers.get_all_ci_metadata")
    def test_get_ci_metadata_v2_with_no_parameters_returns_none(self, mocked_get_all_ci_metadata):
        """
        Why am I testing:
            To check that `None` is returned if no CIs are found when no parameters are supplied.
        What am I testing:
            None is returned when no params are passed
        """
        # Update mocked `get_all_ci_metadata` call to return `None`
        mocked_get_all_ci_metadata.return_value = None

        items = get_ci_metadata_v2(self.query_params)
        assert items is None

    @patch("app.handlers.query_ci_by_status")
    def test_get_ci_metadata_v2_returns_ci_found_when_querying_with_status(self, mocked_query_ci_by_status):
        """
        Why am I testing:
            To check that all the CIs are returned when querying with Status parameter.
        What am I testing:
            Data containing multiple CI is returned when status param is passed
        """
        # Update mocked `get_ci_by_status` call to return list of valid ci
        mocked_query_ci_by_status.return_value = self.mock_ci_list

        # Update `query_params` to include valid `status`
        self.query_params.status = self.mock_status

        items = get_ci_metadata_v2(self.query_params)
        assert items == self.mock_ci_list

    # Test for survey_id, language, form_type and status params
    @patch("app.handlers.query_ci_metadata")
    def test_get_ci_metadata_v2_returns_ci_found_when_querying_survey_lan_formtype_status(self, mocked_query_ci_metadata):
        """
        Why am I testing:
            To check that CIs are returned when survey_id, form_type, language, and status are
            supplied.
        What am I testing:
            Data containing multiple CI is returned when survey_id, form_type, language, and status
            are passed
        """
        # Update mocked `query_ci_metadata` call to return list of valid ci
        mocked_query_ci_metadata.return_value = self.mock_ci_list

        # Update `query_params` to include all valid params
        self.query_params.form_type = self.mock_form_type
        self.query_params.language = self.mock_language
        self.query_params.status = self.mock_status
        self.query_params.survey_id = self.mock_survey_id

        items = get_ci_metadata_v2(self.query_params)
        assert items == self.mock_ci_list

    # Test for survey_id, language, form_type params
    @patch("app.handlers.query_ci_metadata")
    def test_get_ci_metadata_v2_returns_ci_found_when_querying_with_survey_lan_formtype(self, mocked_query_ci_metadata):
        """
        Why am I testing:
            To check that CIs are returned when survey_id, form_type, and language are supplied.
        What am I testing:
            Data containing multiple CI is returned when survey_id, form_type, and language are passed
        """
        # Update mocked `query_ci_metadata` call to return list of valid ci
        mocked_query_ci_metadata.return_value = self.mock_ci_list

        # Update `query_params` to include survey_id, language, form_type params
        self.query_params.form_type = self.mock_form_type
        self.query_params.language = self.mock_language
        self.query_params.survey_id = self.mock_survey_id

        items = get_ci_metadata_v2(self.query_params)
        assert items == self.mock_ci_list


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


@patch("app.handlers.update_ci_metadata_status_to_published")
@patch("app.handlers.query_ci_metadata_with_guid")
class TestUpdateStatusV2:
    """Tests for the `put_status_v1` handler"""

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

    query_params = PutStatusV2Params(id=mock_id)

    def test_handler_calls_query_ci_with_guid_and_update_ci(
        self, mocked_query_ci_metadata_with_guid, mocked_update_ci_metadata_status_to_published
    ):
        """
         `put_status_v1` should call `query_ci_metadata_with_guid`and `update_ci_metadata_status_to_published`
        to update the status of CI
        """
        ci_metadata = {"status": Status.DRAFT.value}
        mocked_query_ci_metadata_with_guid.return_value = ci_metadata
        put_status_v1(self.query_params)
        mocked_query_ci_metadata_with_guid.assert_called_once()
        mocked_update_ci_metadata_status_to_published.assert_called_once()

    def test_handler_calls_query_ci_with_guid_and_update_ci_with_right_inputs(
        self, mocked_query_ci_metadata_with_guid, mocked_update_ci_metadata_status_to_published
    ):
        """
        `put_status_v1` should call `query_ci_metadata_with_guid`and `update_ci_metadata_status_to_published`
         to update the status of CI with right inputs
        """

        ci_metadata = {"status": Status.DRAFT.value}
        mocked_query_ci_metadata_with_guid.return_value = ci_metadata
        put_status_v1(self.query_params)

        # Assert that query_ci_metadata_with_guid was called with the correct parameter
        mocked_query_ci_metadata_with_guid.assert_called_once_with(self.query_params.id)

        # Assert that update_ci_metadata_status_to_published was called with the correct parameters
        mocked_update_ci_metadata_status_to_published.assert_called_once_with(
            self.query_params.id, {"status": Status.PUBLISHED.value}
        )

    def test_handler_returns_right_output_of_query_ci_with_guid_and_update_ci_if_status_DRAFT(
        self, mocked_query_ci_metadata_with_guid, mocked_update_ci_metadata_status_to_published
    ):
        """
        `put_status_v1` should return right output of `query_ci_metadata_with_guid`and
        `update_ci_metadata_status_to_published` once status of CI is updated
        """
        ci_metadata = {"status": Status.DRAFT.value}
        mocked_query_ci_metadata_with_guid.return_value = ci_metadata
        response_ci, status = put_status_v1(self.query_params)
        assert response_ci == ci_metadata
        assert status is True

    def test_handler_returns_right_output_of_query_ci_with_guid_and_update_ci_if_status_PUBLISHED(
        self, mocked_query_ci_metadata_with_guid, mocked_update_ci_metadata_status_to_published
    ):
        """
        `put_status_v1` should return output `query_ci_metadata_with_guid` and
        `update_ci_metadata_status_to_published` if status of CI is already updated

        """
        ci_metadata = {"status": Status.PUBLISHED.value}
        mocked_query_ci_metadata_with_guid.return_value = ci_metadata
        status = put_status_v1(self.query_params)
        response_ci, status = put_status_v1(self.query_params)
        assert response_ci == ci_metadata
        assert status is False
