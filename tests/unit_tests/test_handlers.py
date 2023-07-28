from unittest.mock import patch
from app.handlers import get_ci_metadata_v1, get_ci_metadata_v2, delete_ci_v1, post_ci_metadata_v1
from app.models.requests import GetCiMetadataV1Params, GetCiMetadataV2Params, DeleteCiV1Params, PostCiMetadataV1Params


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
    query_params = GetCiMetadataV2Params(form_type=None, language=None, status=None, survey_id=None)
    # type ignore [arg-type]

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
    def test_get_ci_metadata_v2_returns_ci_found_when_querying_survey_lan_form_type_status(self, mocked_query_ci_metadata):
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
    def test_get_ci_metadata_v2_returns_ci_found_when_querying_with_survey_lan_form_type(self, mocked_query_ci_metadata):
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


# @patch("app.handlers.delete_ci_v1")
class TestHttpDeleteCiV1:
    mock_form_type = "t"
    mock_language = "em"
    mock_survey_id = 12124141

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
        `delete_ci_metadata_v1` should call `query_ci_by_survey_id`
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


class TestHttpPostCiV1:
    mock_survey_id = "12124141"
    mock_language = "em"
    mock_form_type = "t"
    mock_title = "test"
    mock_schema_version = "12"
    mock_data_version = "1"
    mock_sds_schema = ""

    mock_ci_metadata = {
        "data_version": "1",
        "form_type": mock_form_type,
        "language": mock_language,
        "schema_version": "12",
        "survey_id": mock_survey_id,
        "title": "test",
    }

    query_params = PostCiMetadataV1Params(
        survey_id=mock_survey_id,
        language=mock_language,
        form_type=mock_form_type,
        title=mock_title,
        schema_version=mock_schema_version,
        data_version=mock_data_version,
        sds_schema=mock_sds_schema,
    )

    @patch("app.handlers.post_ci_metadata")
    def test_handler_calls_post_ci_metadata(self, mocked_post_ci_metadata):
        """
        `get_ci_metadata_v1` should call `query_ci_metadata` to query the database for ci metadata
        """
        post_ci_metadata_v1(self.query_params)
        mocked_post_ci_metadata.assert_called_once()

    @patch("app.handlers.post_ci_metadata")
    def test_handler_calls_query_ci_by_survey_id_with_correct_inputs(self, mocked_post_ci_metadata):
        """
        `delete_ci_metadata_v1` should call `query_ci_by_survey_id`
        """

        post_ci_metadata_v1(self.query_params)
        mocked_post_ci_metadata.assert_called_with(self.mock_survey_id)

    @patch("app.handlers.store_ci_schema")
    def test_handler_calls_delete_ci_schema(self, mocked_store_ci_schema):
        """
        `get_ci_metadata_v1` should call `query_ci_metadata` to query the database for ci metadata
        """
        post_ci_metadata_v1(self.query_params)
        mocked_store_ci_schema.assert_called_once()

    @patch("app.handlers.store_ci_schema")
    def test_handler_calls_delete_ci_schema_with_correct_inputs(self, mocked_store_ci_schema):
        """
        `delete_ci_schema_v1` should call `delete ci schema'
        """
        post_ci_metadata_v1(self.query_params)
        mocked_store_ci_schema.assert_called_with(self.mock_survey_id)
