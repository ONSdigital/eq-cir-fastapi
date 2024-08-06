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
        self.publisher = PublisherClient()
        self.topic_path = self.publisher.topic_path(settings.PROJECT_ID, settings.TOPIC_ID)

    def publish_message(self, event_msg: PostCIEvent) -> None:
        """Publishes an event message to a Pub/Sub topic."""

        # Verify if the topic exists - if not, raise an exception
        self._verify_topic_exists()

        # Convert the event object to a JSON string using `model_dump`, which exlcudes `sds_schema`
        # key if this field is not filled
        data_str = json.dumps(event_msg.model_dump())

        # Data must be a bytestring
        data = data_str.encode("utf-8")

        # Publishes a message
        try:
            future = self.publisher.publish(self.topic_path, data=data)
            result = future.result()  # Verify the publish succeeded
            logger.debug(f"Message published. {result}")
        except Exception as e:
            logger.debug(e)

    def _verify_topic_exists(self) -> None:
        """
        If the topic does not exist raises 500 global error.
        """
        try:
            self.create_topic()
            self.publisher.get_topic(request={"topic": self.topic_path})
        except Exception:
            logger.debug("Error getting topic")
            raise ExceptionTopicNotFound

    def create_topic(self) -> None:
        """Create a new Pub/Sub topic."""
        logger.debug("create_topic")
        topic = self.publisher.create_topic(request={"name": self.topic_path})
        logger.debug(f"Created topic: {topic.name}")


publisher = Publisher()
