import json

from google.cloud.pubsub_v1 import PublisherClient

from app.config import Settings, logging
from app.exception.exceptions import ExceptionTopicNotFound
from app.models.events import PostCIEvent

logger = logging.getLogger(__name__)
settings = Settings()


class Publisher:
    """Methods to publish pub/sub messages using the `pubsub_v1.PublisherClient()`"""

    def __init__(self) -> None:
        self.publisher_client = self._init_client()

    def _init_client(self) -> None | PublisherClient:
        """Initializes the Pub/Sub client."""
        if settings.CONF == "unit":
            return None
        else:
            return PublisherClient()

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
            result = future.result()  # Verify the publish succeeded
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
            raise ExceptionTopicNotFound from exc


publisher = Publisher()
