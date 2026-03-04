import json

import pytest

from app.config import Settings
from app.events.publisher import Publisher
from app.exception.exceptions import ExceptionTopicNotFound

from app.models.responses import CiMetadata
from google.cloud import exceptions


settings = Settings()


mock_event_message = CiMetadata(
    ci_version=1,
    data_version="0.1",
    validator_version="0.0.1",
    classifier_type="form_type",
    classifier_value="005",
    guid="202020",
    language="en",
    published_at="timestamp",
    sds_schema="",
    survey_id="345",
    title="survey",
)


class TestPublisher:

    def test_publish_message_success(self, mocker):
        mocked_publisher_client = mocker.Mock()
        mocker.patch("app.config.settings.PROJECT_ID", "project_id")
        mocker.patch("app.config.settings.PUBLISH_CI_TOPIC_ID", "topic_id")

        mock_topic_exists = mocker.patch("app.events.publisher.Publisher._verify_topic_exists")
        mock_logger = mocker.patch("logging.Logger.debug")
        mock_future = mocked_publisher_client.publish.return_value
        mock_future.result.return_value = "success"
        mocked_publisher_client.topic_path.return_value = "project_id/topics/topic_id"

        data_str = json.dumps(mock_event_message.model_dump())
        data = data_str.encode("utf-8")

        publisher = Publisher(mocked_publisher_client)
        publisher.publish_message(mock_event_message)
        mock_topic_exists.assert_called_once()
        mocked_publisher_client.publish.assert_called_once_with("project_id/topics/topic_id", data=data)
        mock_future.result.assert_called_once()
        expected_message = "Message published. success"
        actual_message = mock_logger.call_args[0][0]
        assert actual_message == expected_message

    def test_publish_message_failure(self, mocker):
        mocked_publisher_client = mocker.Mock()
        mock_logger = mocker.patch("app.config.logging.Logger.debug")
        # Mock the create_topic method to raise an exception
        mocked_publisher_client.publish.side_effect = RuntimeError("Error publishing message")

        publisher = Publisher(mocked_publisher_client)
        with pytest.raises(Exception):
            publisher.publish_message(mock_event_message)

        # Assert that the logger were called
        mock_logger.assert_called_once()

        # Assert that the logger.debug method was called with the exception
        expected_error_message = "Error publishing message"
        actual_error_message = str(mock_logger.call_args[0][0].args[0])
        assert actual_error_message == expected_error_message

    def test_verify_topic_success_when_topic_exists(self, mocker):
        mocked_publisher_client = mocker.Mock()
        mocked_publisher_client.topic_path.return_value = "project_id/topics/topic_id"

        publisher = Publisher(mocked_publisher_client)
        result = publisher._verify_topic_exists("project_id/topics/topic_id")

        mocked_publisher_client.get_topic.assert_called_once_with(request={"topic": "project_id/topics/topic_id"})
        assert result

    def test_verify_topic_raise_exception_when_topic_not_found(self, mocker):
        mocked_publisher_client = mocker.Mock()
        mocked_publisher_client.get_topic.side_effect = exceptions.NotFound("Topic not found")

        publisher = Publisher(mocked_publisher_client)

        with pytest.raises(ExceptionTopicNotFound):
            publisher._verify_topic_exists("")
