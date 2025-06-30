import json
from unittest.mock import patch

import pytest

from app.config import Settings
from app.events.publisher import Publisher
from app.exception.exceptions import ExceptionTopicNotFound
from app.models.events import PostCIEvent

settings = Settings()


mock_event_message = PostCIEvent(
    ci_version=1,
    data_version="0.1",
    validator_version="0.0.1",
    classifier_type="form_type",
    classifier_value="005",
    guid="202020",
    language="en",
    published_at="timestamp",
    sds_schema="",
    status="DRAFT",
    survey_id="345",
    title="survey",
)


@patch("app.events.publisher.Publisher._init_client")
class TestPublisher:
    def test_publish_message_success(self, mocked_publisher_client, mocker):
        mocker.patch("app.config.settings.PROJECT_ID", "project_id")
        mocker.patch("app.config.settings.PUBLISH_CI_TOPIC_ID", "topic_id")

        mock_topic_exists = mocker.patch("app.events.publisher.Publisher._verify_topic_exists")
        mock_logger = mocker.patch("logging.Logger.debug")
        mock_future = mocked_publisher_client.return_value.publish.return_value
        mock_future.result.return_value = "success"
        mocked_publisher_client.return_value.topic_path.return_value = "project_id/topics/topic_id"

        data_str = json.dumps(mock_event_message.model_dump())
        data = data_str.encode("utf-8")

        publisher = Publisher()
        publisher.publish_message(mock_event_message)
        mock_topic_exists.assert_called_once()
        mocked_publisher_client.return_value.publish.assert_called_once_with("project_id/topics/topic_id", data=data)
        mock_future.result.assert_called_once()
        expected_message = "Message published. success"
        actual_message = mock_logger.call_args[0][0]
        assert actual_message == expected_message

    def test_publish_message_failure(self, mocked_publisher_client, mocker):
        mock_logger = mocker.patch("app.config.logging.Logger.debug")
        # Mock the create_topic method to raise an exception
        mocked_publisher_client.return_value.publish.side_effect = Exception("Error publishing message")

        publisher = Publisher()
        publisher.publish_message(mock_event_message)

        # Assert that the logger were called
        mock_logger.assert_called_once()

        # Assert that the logger.debug method was called with the exception
        expected_error_message = "Error publishing message"
        actual_error_message = str(mock_logger.call_args[0][0].args[0])
        assert actual_error_message == expected_error_message

    def test_topic_exists_success(self, mocked_publisher_client):
        mocked_publisher_client.return_value.topic_path.return_value = "project_id/topics/topic_id"

        publisher = Publisher()
        result = publisher._verify_topic_exists("project_id/topics/topic_id")

        mocked_publisher_client.return_value.get_topic.assert_called_once_with(request={"topic": "project_id/topics/topic_id"})
        assert result

    def test_topic_exists_failure(self, mocked_publisher_client):
        mocked_publisher_client.return_value.get_topic.side_effect = Exception

        publisher = Publisher()

        with pytest.raises(ExceptionTopicNotFound):
            publisher._verify_topic_exists("")
