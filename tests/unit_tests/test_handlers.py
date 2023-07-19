from unittest.mock import patch

from app.handlers import get_ci_metadata_v1, get_ci_metadata_v2
from app.models.requests import GetCiMetadataV1Params


@patch("app.handlers.query_ci_metadata")
class TestGetCiMetadataV1:
    """
    Tests for the `get_ci_metadata_v1` handler

    Calls to `app.repositories.firestore.query_ci_metadata` are mocked out for these tests
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
    mock_request_data = {
        "survey_id": mock_survey_id,
        "language": mock_language,
        "form_type": mock_form_type,
        "title": mock_title,
        "schema_version": mock_schema_version,
        "data_version": mock_data_version,
    }

    @patch("app.handlers.get_all_ci_metadata")
    def test_get_ci_metadata_v2_with_no_parameters_with_200_status(self, mocked_get_all_ci_metadata):
        """
        Why am I testing:
            To check that all the CIs are returned when no parameters are supplied.
        What am I testing:
            Data containing multiple CI is returned when no params are passed
        """

        mock_ci_list = [
            {
                "survey_id": self.mock_survey_id,
                "form_type": self.mock_form_type,
                "language": self.mock_language,
                "title": "test1",
                "ci_version": 1,
            },
            {
                "survey_id": self.mock_survey_id,
                "form_type": self.mock_form_type,
                "language": self.mock_language,
                "title": "test2",
                "ci_version": 2,
            },
        ]

        mocked_get_all_ci_metadata.return_value = mock_ci_list

        mock_request = MockRequestArgs(mock_request)
        items = get_ci_metadata_v2(mock_request)
        expected_response = (
            good_response_200(mock_ci_list),
            200,
        )

        assert expected_response == items

    def test_get_ci_metadata_v2_with_no_parameters_with_404_status(mocker):
        """
        Why am I testing:
            To check that a 404 error is returned if no CI's exist.
        What am I testing:
                404 that the CI could not be found and a "message": "No CI metadata found."
        """

        mock_request = {}

        mocker.patch(
            "src.handlers.collection_instrument.get_all_ci_metadata",
            return_value=None,
        )

        mock_request = MockRequestArgs(mock_request)
        items = get_ci_metadata_v2(mock_request)
        expected_response = (
            bad_request(
                f"No CI metadata found for {mock_request.args}",
            ),
            404,
        )
        assert expected_response == items

    # Test for status param ONLY

    def test_get_ci_metadata_v2_returns_ci_found_when_querying_with_status_return_200(mocker):
        """
        Why am I testing:
            To check that all the CIs are returned when querying with Status parameter.
        What am I testing:
            200 success message and data containing multiple CI is returned when status param is passed
        """
        mock_request = {
            "status": mock_status,
        }
        mock_ci_list = [
            {
                "survey_id": mock_survey_id,
                "form_type": mock_form_type,
                "language": mock_language,
                "title": "test1",
                "ci_version": 1,
                "status": mock_status,
            },
            {
                "survey_id": mock_survey_id,
                "form_type": mock_form_type,
                "language": mock_language,
                "title": "test2",
                "ci_version": 2,
                "status": mock_status,
            },
        ]
        mocker.patch(
            "src.handlers.collection_instrument.query_ci_by_status",
            return_value=mock_ci_list,
        )
        mock_request = MockRequestArgs(mock_request)
        items = get_ci_metadata_v2(mock_request)
        expected_resp = (good_response_200(mock_ci_list), 200)
        assert items == expected_resp

    def test_get_ci_metadata_v2_returns_ci_not_found_when_querying_with_status_return_404(mocker):
        """
        Why am I testing:
            To check that a 404 error is returned if no CI's exist.
        What am I testing:
                404 that the CI could not be found and a "message": "No CI metadata found."
        """
        mock_request = {
            "status": mock_status,
        }

        mocker.patch(
            "src.handlers.collection_instrument.query_ci_by_status",
            return_value=None,
        )
        mock_request = MockRequestArgs(mock_request)
        items = get_ci_metadata_v2(mock_request)
        expected_resp = (
            bad_request(
                f"No CI metadata found for {mock_request.args}",
            ),
            404,
        )
        assert items == expected_resp

    # Test for survey_id, language, form_type and status params

    def test_get_ci_metadata_v2_returns_ci_found_when_querying_survey_lan_formtype_status_return_200(mocker):
        """
        Why am I testing:
            To check that CIs are returned when survey_id, form_type, language, and status are supplied.
        What am I testing:
            200 success message and data containing multiple CI is returned when survey_id, form_type,
            language, and status are passed
        """

        mock_request = {
            "survey_id": mock_survey_id,
            "form_type": mock_form_type,
            "language": mock_language,
            "status": mock_status,
        }
        mock_ci_list = [
            {
                "survey_id": mock_survey_id,
                "form_type": mock_form_type,
                "language": mock_language,
                "title": "test1",
                "ci_version": 1,
                "status": mock_status,
            },
            {
                "survey_id": mock_survey_id,
                "form_type": mock_form_type,
                "language": mock_language,
                "title": "test2",
                "ci_version": 2,
                "status": mock_status,
            },
        ]
        mocker.patch(
            "src.handlers.collection_instrument.query_ci_metadata",
            return_value=mock_ci_list,
        )
        mock_request = MockRequestArgs(mock_request)
        items = get_ci_metadata_v2(mock_request)

        expected_resp = (good_response_200(mock_ci_list), 200)
        assert items == expected_resp

    def test_get_ci_metadata_v2_returns_ci_not_found_when_querying_survey_lan_formtype_status_return_404(mocker):
        """
        Why am I testing:
            To check that there is no CI available by survey_id, form_type,language and status.
            It should 404 that the CI could not be found.
        What am I testing:
        404 that the CI could not be found and a "message": "No CI metadata found for <survey_id> ,
        <form_type>, <language>, <status> and <version>"
        """
        mock_request = {
            "survey_id": mock_survey_id,
            "form_type": mock_form_type,
            "language": mock_language,
            "status": mock_status,
        }
        mocker.patch(
            "src.handlers.collection_instrument.query_ci_metadata",
            return_value=None,
        )
        mock_request = MockRequestArgs(mock_request)
        items = get_ci_metadata_v2(mock_request)

        expected_resp = (
            bad_request(
                f"No CI metadata found for {mock_request.args}",
            ),
            404,
        )
        assert items == expected_resp

    # Test for survey_id, language, form_type params
    def test_get_ci_metadata_v2_returns_ci_found_when_querying_with_survey_lan_formtype_returns_200(mocker):
        """
        Why am I testing:
            To check that CIs are returned when survey_id, form_type, and language are supplied.
        What am I testing:
            200 success message and data containing multiple CI is returned when survey_id, form_type, and language are passed
        """

        mock_request = {
            "survey_id": mock_survey_id,
            "form_type": mock_form_type,
            "language": mock_language,
        }
        mock_ci_list = [
            {
                "survey_id": mock_survey_id,
                "form_type": mock_form_type,
                "language": mock_language,
                "title": "test1",
                "ci_version": 1,
                "status": mock_status,
            },
            {
                "survey_id": mock_survey_id,
                "form_type": mock_form_type,
                "language": mock_language,
                "title": "test2",
                "ci_version": 2,
                "status": mock_status,
            },
        ]

        mocker.patch(
            "src.handlers.collection_instrument.query_ci_metadata",
            return_value=mock_ci_list,
        )
        mock_request = MockRequestArgs(mock_request)
        items = get_ci_metadata_v2(mock_request)
        expected_response = (
            good_response_200(mock_ci_list),
            200,
        )
        assert expected_response == items

    def test_get_ci_metadata_v2_returns_ci_not_found_when_querying_with_survey_lan_formtype_returns_404(mocker):
        """
        Why am I testing:
            To check that there is no CI available by survey_id, form_type, and language.
            It should 404 that the CI could not be found.
        What am I testing:
        404 that the CI could not be found and a "message": "No CI metadata found for <survey_id> ,
        <form_type> and <version>"}
        """
        mock_request = {
            "survey_id": mock_survey_id,
            "form_type": mock_form_type,
            "language": mock_language,
        }

        mocker.patch(
            "src.handlers.collection_instrument.query_ci_metadata",
            return_value=None,
        )
        mock_request = MockRequestArgs(mock_request)
        items = get_ci_metadata_v2(mock_request)
        expected_response = (
            bad_request(
                f"No CI metadata found for {mock_request.args}",
            ),
            404,
        )
        assert expected_response == items

    def test_get_ci_metadata_v2_returns_returns_400_with_bad_parameter_set(mocker):
        """
        Why am I testing:
            To check that when an incorrect parameter set is passed,
            it should 404 that the CI could not be found.
        What am I testing:
        400 and a "message": "Bad query parameters"
        """
        mock_request = {
            "survey_id": mock_survey_id,
            "form_type": mock_form_type,
        }

        mocker.patch(
            "src.handlers.collection_instrument.query_ci_metadata",
            return_value=None,
        )
        mock_request = MockRequestArgs(mock_request)
        items = get_ci_metadata_v2(mock_request)
        expected_response = (
            bad_request(
                "Bad query parameters",
            ),
            400,
        )
        assert expected_response == items
