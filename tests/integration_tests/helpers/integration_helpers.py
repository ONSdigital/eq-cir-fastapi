import time

from tests.integration_tests.helpers.pubsub_helper import PubSubHelper


def pubsub_setup(pubsub_helper: PubSubHelper, subscriber_id: str) -> None:
    """Creates any subscribers that may be used in tests"""
    pubsub_helper.try_create_subscriber(subscriber_id)


def pubsub_teardown(pubsub_helper: PubSubHelper, subscriber_id: str) -> None:
    """Deletes subscribers that may have been used in tests"""
    pubsub_helper.try_delete_subscriber(subscriber_id)


def pubsub_purge_messages(pubsub_helper: PubSubHelper, subscriber_id: str) -> None:
    """Purge any messages that may have been sent to a subscriber"""
    pubsub_helper.purge_messages(subscriber_id)


def inject_wait_time(seconds: int) -> None:
    """
    Method to inject a wait time into the test to allow resources properly spin up and tear down.

    Parameters:
        seconds: the number of seconds to wait

    Returns:
        None
    """
    time.sleep(seconds)
