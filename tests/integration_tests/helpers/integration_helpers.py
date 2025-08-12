import datetime

from app.config import settings
from tests.integration_tests.helpers.pubsub_helper import PubSubHelper


def subscriber_setup(pubsub_helper: PubSubHelper, subscriber_id: str) -> None:
    """Creates any subscribers that may be used in tests"""
    pubsub_helper.try_create_subscriber(subscriber_id)


def subscriber_teardown(pubsub_helper: PubSubHelper, subscriber_id: str) -> None:
    """Deletes subscribers that may have been used in tests"""
    pubsub_helper.try_delete_subscriber(subscriber_id)


def pubsub_purge_messages(pubsub_helper: PubSubHelper, subscriber_id: str) -> None:
    """Purge any messages that may have been sent to a subscriber"""
    pubsub_helper.purge_messages(subscriber_id)


def generate_subscriber_id() -> str:
    """Generates a unique subscriber id for each test"""
    suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    return f"{settings.SUBSCRIPTION_ID}-{suffix}"
