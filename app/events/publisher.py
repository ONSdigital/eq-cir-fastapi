import json

from google.cloud.pubsub_v1 import PublisherClient

from app.config import Settings, logging
from app.exception.exceptions import ExceptionTopicNotFound
from app.models.events import PostCIEvent

logger = logging.getLogger(__name__)
settings = Settings()


class Publisher:
    """Methods to publish pub/sub messages using the `pubsub_v1.PublisherClient()`"""

    def __init__(self, publisher_client: PublisherClient) -> None:
        self.publisher_client = publisher_client

        if settings.CONF == "unit":
            return

        topic_path = self.publisher_client.topic_path(settings.PROJECT_ID, settings.PUBLISH_CI_TOPIC_ID)

        # In local docker, we create the topic if it does not exist
        if settings.CONF == "local-docker" and not self._verify_topic_exists(topic_path):
            self._create_topic(topic_path)

    def publish_message(self, event_msg: PostCIEvent) -> None:
        """Publishes an event message to a Pub/Sub topic."""

        # Get the topic path
        topic_path = self.publisher_client.topic_path(settings.PROJECT_ID, settings.PUBLISH_CI_TOPIC_ID)
        # Verify if the topic exists - if not, raise an exception
        self._verify_topic_exists(topic_path)

        # Convert the event object to a JSON string using `model_dump`, which excludes `sds_schema`
        # key if this field is not filled
        data_str = json.dumps(event_msg.model_dump())

        # Data must be a bytestring
        data = data_str.encode("utf-8")

        # Publishes a message
        try:
            future = self.publisher_client.publish(topic_path, data=data)
            result = future.result()  # Verify the publishing succeeded
            logger.debug(f"Message published. {result}")
        except Exception as e:
            logger.debug(e)

    def _verify_topic_exists(self, topic_path: str) -> bool:
        """
        If the topic does not exist raises 500 global error.
        """
        try:
            self.publisher_client.get_topic(request={"topic": topic_path})
            return True
        except Exception as exc:
            logger.debug("Error getting topic")

            if settings.CONF == "local-docker":
                return False

            raise ExceptionTopicNotFound from exc

    def _create_topic(self, topic_path: str) -> None:
        """Creates a Pub/Sub topic."""
        try:
            self.publisher_client.create_topic(request={"name": topic_path})
            logger.debug(f"Topic created: {topic_path}")
        except Exception as exc:
            raise Exception("Error creating topic") from exc


publisher = Publisher(PublisherClient())
