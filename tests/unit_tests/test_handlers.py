import datetime
import uuid
from unittest.mock import patch

from app.handlers import (
    delete_ci_v1,
    get_ci_metadata_v1,
    get_ci_metadata_v2,
    post_ci_metadata_v1,
)
from app.models.requests import (
    DeleteCiV1Params,
    GetCiMetadataV1Params,
    GetCiMetadataV2Params,
    PostCiMetadataV1PostData,
)
from app.models.responses import CiMetadata, CiStatus

# Mock data for all tests
mock_data_version = "1"
mock_form_type = "t"
mock_language = "em"
mock_schema_version = "12"
mock_status = "DRAFT"
mock_survey_id = "12124141"
mock_title = "test"

mock_ci_metadata = CiMetadata(
    ci_version=1,
    data_version="1",
    form_type=mock_form_type,
    id=str(uuid.uuid4()),
    language=mock_language,
    published_at=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    schema_version=mock_schema_version,
    sds_schema="",
    status=CiStatus.DRAFT.value,
    survey_id=mock_survey_id,
    title="test",
)


@patch("app.handlers.query_ci_metadata")
class TestGetCiMetadataV1:
    """
    Tests for the `get_ci_metadata_v1` handler

    All calls to `app.repositories.firestore.query_ci_metadata` are mocked out for these tests
    """

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
        mocked_query_ci_metadata.assert_called_with(
            self.query_params.survey_id, self.query_params.form_type, self.query_params.language
        )

    def test_handler_returns_output_of_query_ci_metadata(self, mocked_query_ci_metadata):
        """
        `get_ci_metadata_v1` should return the output of `query_ci_metadata`
        """
        # Update mocked `query_ci_metadata` to return valid ci metadata
        mocked_query_ci_metadata.return_value = mock_ci_metadata
        response = get_ci_metadata_v1(self.query_params)

        assert response == mock_ci_metadata


class TestGetCiMetadataV2:
    """Tests for the `get_ci_metadata_v2` handler"""

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
        self.query_params.status = mock_status

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
        self.query_params.form_type = mock_form_type
        self.query_params.language = mock_language
        self.query_params.status = mock_status
        self.query_params.survey_id = mock_survey_id

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
        self.query_params.form_type = mock_form_type
        self.query_params.language = mock_language
        self.query_params.survey_id = mock_survey_id

        items = get_ci_metadata_v2(self.query_params)
        assert items == self.mock_ci_list


@patch("app.handlers.db")
@patch("app.handlers.delete_ci_metadata")
@patch("app.handlers.delete_ci_schema")
@patch("app.handlers.query_ci_by_survey_id")
class TestDeleteCiV1:
    """
    Tests for the `delete_ci_v1` handler
    Calls to `db.transaction()`, `delete_ci_metadata`, `delete_ci_schema` and
    `query_ci_by_survey_id` are mocked out for these tests
    """

    query_params = DeleteCiV1Params(survey_id=mock_survey_id)

    def test_handler_calls_query_ci_by_survey_id(
        self, mocked_query_ci_by_survey_id, mocked_delete_ci_schema, mocked_delete_ci_metadata, mocked_db
    ):
        """
        `delete_ci_metadata_v1` should call `query_ci_by_survey_id`
        """

        delete_ci_v1(self.query_params)
        mocked_query_ci_by_survey_id.assert_called_once()

    def test_handler_calls_query_ci_by_survey_id_with_correct_inputs(
        self, mocked_query_ci_by_survey_id, mocked_delete_ci_schema, mocked_delete_ci_metadata, mocked_db
    ):
        """
        `delete_ci_metadata_v1` should call `query_ci_by_survey_id` with the correct `survey_id` input
        """

        delete_ci_v1(self.query_params)
        mocked_query_ci_by_survey_id.assert_called_with(self.query_params.survey_id)

    def test_handler_returns_none_if_ci_not_found(
        self, mocked_query_ci_by_survey_id, mocked_delete_ci_schema, mocked_delete_ci_metadata, mocked_db
    ):
        """
        `delete_ci_metadata_v1` should return `None` if no valid ci are found when calling
        `query_ci_by_survey_id`
        """
        # Configure `query_ci_by_survey_id` to return an empty list showing no ci have been found
        mocked_query_ci_by_survey_id.return_value = []

        return_value = delete_ci_v1(self.query_params)

        assert return_value is None

    def test_handler_calls_delete_ci_metadata_delete_ci_schema(
        self, mocked_query_ci_by_survey_id, mocked_delete_ci_schema, mocked_delete_ci_metadata, mocked_db
    ):
        """
        `get_ci_metadata_v1` should call `delete_ci_metadata` and `delete_ci_schema` to delete ci
        metadata and schema if valid ci are found by `query_ci_by_survey_id`
        """
        # Configure `query_ci_by_survey_id` to return a list of valid ci
        mocked_query_ci_by_survey_id.return_value = [mock_ci_metadata]

        delete_ci_v1(self.query_params)
        # Confirm `delete_ci_metadata` and `delete_ci_schema` are called
        mocked_db.transaction.assert_called_once()
        mocked_delete_ci_metadata.assert_called_once()
        mocked_delete_ci_schema.assert_called_once()

    def test_handler_calls_delete_ci_metadata_delete_ci_schema_with_correct_inputs(
        self, mocked_query_ci_by_survey_id, mocked_delete_ci_schema, mocked_delete_ci_metadata, mocked_db
    ):
        """
        `get_ci_metadata_v1` should call `delete_ci_metadata` and `delete_ci_schema` to delete ci
        metadata and schema if valid ci are found by `query_ci_by_survey_id`
         * `delete_ci_metadata` should be called with the valid `survey_id`
         * `delete_ci_schema` should be called with a list of valid ci
        """
        # Configure `query_ci_by_survey_id` to return a list of valid ci
        mocked_query_ci_by_survey_id.return_value = [mock_ci_metadata]

        delete_ci_v1(self.query_params)
        # Confirm `delete_ci_metadata` and `delete_ci_schema` are called with the correct inputs
        mocked_delete_ci_metadata.assert_called_with(self.query_params.survey_id)
        mocked_delete_ci_schema.assert_called_with([mock_ci_metadata])


@patch("app.handlers.db")
@patch("app.handlers.post_ci_metadata")
@patch("app.handlers.store_ci_schema")
class TestHttpPostCiMetadataV1:
    """
    Tests for the `post_ci_metadata_v1` handler
    Calls to `db.transaction()`, `post_ci_metadata` and `store_ci_schema` are mocked out for these
    tests
    """

    post_data = PostCiMetadataV1PostData(
        survey_id=mock_survey_id,
        language=mock_language,
        form_type=mock_form_type,
        title=mock_title,
        schema_version=mock_schema_version,
        data_version=mock_data_version,
    )

    def test_handler_calls_post_ci_metadata(self, mocked_store_ci_schema, mocked_post_ci_metadata, mocked_db):
        """
        `delete_ci_metadata_v1` should call `post_ci_metadata` to write metadata to the firestore
        db
        """
        post_ci_metadata_v1(self.post_data)
        mocked_post_ci_metadata.assert_called_once()

    def test_handler_calls_post_ci_metadata_with_correct_inputs(
        self, mocked_store_ci_schema, mocked_post_ci_metadata, mocked_db
    ):
        """
        `delete_ci_metadata_v1` should call `post_ci_metadata` to write metadata to the firestore
        db. It should be called with the input post data model
        """

        post_ci_metadata_v1(self.post_data)
        mocked_post_ci_metadata.assert_called_with(self.post_data)

    def test_handler_calls_store_ci_schema(self, mocked_store_ci_schema, mocked_post_ci_metadata, mocked_db):
        """
        `delete_ci_metadata_v1` should call `store_ci_schema` to write metadata to the firestore db
        """
        post_ci_metadata_v1(self.post_data)
        mocked_store_ci_schema.assert_called_once()

    def test_handler_calls_store_ci_schema_with_correct_inputs(
        self, mocked_store_ci_schema, mocked_post_ci_metadata, mocked_db
    ):
        """
        `delete_ci_metadata_v1` should call `mocked_post_ci_metadata` to write metadata to the
        firestore db. It should be called with the input post data model
        """
        # Configure mocked `post_ci_metadata` to return the the new metadata model
        mocked_post_ci_metadata.return_value = mock_ci_metadata

        post_ci_metadata_v1(self.post_data)
        mocked_store_ci_schema.assert_called_with(mock_ci_metadata.survey_id, self.post_data.__dict__)

    def test_handler_returns_new_ci_metadata_if_creation_successful(
        self, mocked_store_ci_schema, mocked_post_ci_metadata, mocked_db
    ):
        """
        `delete_ci_metadata_v1` should return newly created metadata if creation of ci metadata
        and schema to firestore and cloud storage are successful
        """
        # Configure mocked `post_ci_metadata` to return the the new metadata model
        mocked_post_ci_metadata.return_value = mock_ci_metadata

        return_value = post_ci_metadata_v1(self.post_data)
        assert return_value == mock_ci_metadata

    def test_handler_returns_none_if_exception_raised(self, mocked_store_ci_schema, mocked_post_ci_metadata, mocked_db):
        """
        `delete_ci_metadata_v1` should return `None` if exception is raised at any point during
        the creation of metadata or schema to firestore and cloud storage
        """
        # Configure mocked `post_ci_metadata` to raise a generic exception
        mocked_post_ci_metadata.side_effect = Exception()

        return_value = post_ci_metadata_v1(self.post_data)
        assert return_value is None
