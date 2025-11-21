import datetime
import random
import time

from app.config import settings
from tests.integration_tests.helpers.pubsub_helper import PubSubHelper


def subscriber_setup(pubsub_helper: PubSubHelper, subscriber_id: str) -> None:
    """Creates any subscribers that may be used in tests"""
    pubsub_helper.try_create_subscriber(subscriber_id)


def subscriber_teardown(pubsub_helper: PubSubHelper, subscriber_id: str) -> None:
    """Deletes subscribers that may have been used in tests"""
    pubsub_helper.try_delete_subscriber(subscriber_id)


def generate_subscriber_id() -> str:
    """Generates a random subscriber id for each test"""
    chars_list = random.choices("abcdefghijklmnopqrstuvwxyz", k=4)
    suffix = "".join(chars_list)
    return f"{settings.SUBSCRIPTION_ID}-{suffix}"
