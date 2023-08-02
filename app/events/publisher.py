import json

from google.cloud.pubsub_v1 import PublisherClient

from app.config import Settings, logging
from app.models.events import PostCIEvent

logger = logging.getLogger(__name__)
settings = Settings()


class Publisher:
    """Methods to publish pub/sub messages using the `pubsub_v1.PublisherClient()`"""

    def __init__(self) -> None:
        self.client = PublisherClient()
        self.topic_path = self.client.topic_path(settings.PROJECT_ID, settings.TOPIC_ID)

    def create_topic(self) -> None:
        """Create a new Pub/Sub topic."""

        logger.debug("create_topic")

        try:
            if not self.topic_exists():
                topic = self.client.create_topic(request={"name": self.topic_path})
                logger.debug(f"Created topic: {topic.name}")
        except Exception as e:
            logger.debug(e)

    def publish_message(self, event_msg: PostCIEvent) -> None:
        """Publishes an event message to a Pub/Sub topic."""

        # If topic doesn't already exist, create one
        if not self.topic_exists():
            self.create_topic()

        # Convert the event object to a JSON string
        data_str = json.dumps(event_msg.__dict__)

        # Data must be a bytestring
        data = data_str.encode("utf-8")

        # Publishes a message
        try:
            future = self.client.publish(self.topic_path, data=data)
            result = future.result()  # Verify the publish succeeded
            logger.debug(f"Message published. {result}")
        except Exception as e:
            logger.debug(e)

    def topic_exists(self) -> bool:
        """
        Returns `true` if the topic defined by `self.topic_path` exists otherwise returns `false`.
        """

        try:
            self.client.get_topic(request={"topic": self.topic_path})
            return True
        except Exception as e:
            logger.debug(e)
            return False
