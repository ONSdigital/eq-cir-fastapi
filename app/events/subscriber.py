import logging

from google.cloud.pubsub_v1 import SubscriberClient

from app.config import Settings

logger = logging.getLogger(__name__)
settings = Settings()


class Subscriber:
    """Methods to subscribe to pub/sub messages using the `SubsciberClient()`"""

    def __del__(self) -> None:
        # Make sure we close the client when `Subscriber` is destroyed otherwise multiple clients
        # cause threading issues
        self.client.close()

    def __init__(self) -> None:
        self.client = SubscriberClient()
        self.max_messages = 5
        self.subscription_path = self.client.subscription_path(settings.PROJECT_ID, settings.SUBSCRIPTION_ID)
        self.topic_path = self.client.topic_path(settings.PROJECT_ID, settings.TOPIC_ID)

    def create_subscription(self) -> None:
        """Creates a subscription using `self.subscription_path`"""

        subscription = self.client.create_subscription(
            request={
                "name": self.subscription_path,
                "topic": self.topic_path,
                "enable_message_ordering": True,
            }
        )

        logger.debug(f"Subscription created: {subscription}")

    def delete_subscription(self) -> None:
        """Deletes an existing subscription using `self.subscription_path`"""
        self.client.delete_subscription(request={"subscription": self.subscription_path})

        logger.debug(f"Subscription deleted: {self.subscription_path}.")

    def pull_messages_and_acknowledge(self) -> list:
        """Pulls `self.max_messages` messages from `self.subscription_path` and acknowledges"""
        ack_ids = []
        messages = []

        if not self.subscription_exists():
            self.create_subscription()

        # The subscriber pulls a specific number of messages. The actual
        # number of messages pulled may be smaller than max_messages.
        response = self.client.pull(
            max_messages=self.max_messages,
            return_immediately=True,
            subscription=self.subscription_path,
        )
        if len(response.received_messages) > 0:
            for received_message in response.received_messages:
                logger.debug(f"Received: {received_message.message.data}.")
                messages.append(received_message.message.data)
                ack_ids.append(received_message.ack_id)

            # Acknowledges the received messages so they will not be sent again.
            self.client.acknowledge(request={"subscription": self.subscription_path, "ack_ids": ack_ids})
            logger.info(f"Received and acknowledged {len(response.received_messages)} messages from {self.subscription_path}.")

        else:
            logger.debug("No messages received")

        return messages

    def subscription_exists(self) -> bool:
        """Returns `True` if subscription matching `self.subscription_path` exists, otherwise `False`."""
        try:
            self.client.get_subscription(request={"subscription": self.subscription_path})
            return True
        except Exception:
            return False
