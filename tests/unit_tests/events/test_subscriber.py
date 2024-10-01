from unittest.mock import Mock, patch

from google.pubsub_v1.types import PubsubMessage, PullResponse, ReceivedMessage

from app.events.subscriber import Subscriber

MAX_MESSAGES = 5


@patch("app.events.subscriber.SubscriberClient")
class TestSubscriber:
    """
    Tests for the `Subscriber` class

    We mock out the `SubscriberClient` for all tests to make sure we don't call pub/sub
    """

    # Representative `PubsubMessage` data returned by `Publisher.pull()`
    message_data = {
        "ci_version": 2,
        "data_version": "1",
        "classifier_type": "form_type",
        "classifier_value": "business",
        "id": "ca9c5b88-0700-4e87-a90e-0d3e05ae37d5",
        "language": "welsh",
        "published_at": "2023-06-14T08:54:27.722250Z",
        "schema_version": "1",
        "status": "DRAFT",
        "survey_id": "3456",
        "title": "NotDune",
    }

    def test_init_sets_max_messages_to_five(self, _):
        """
        `__init__` method should assign a value to `self.max_messages`
        This is the number of messages to pull and acknowledge each time
        """

        subscriber = Subscriber()
        assert subscriber.max_messages == MAX_MESSAGES

    def test_init_sets_subscription_path(self, mocked_subscriber_client):
        """
        `__init__` method should assign a value to `self.subscription_path` by calling
        `SubscriberClient.subscription_path`
        """
        subscription_path_value = "test-subscription-path"
        mocked_subscriber_client.return_value.subscription_path.return_value = subscription_path_value

        subscriber = Subscriber()
        assert subscriber.subscription_path == subscription_path_value

    def test_init_sets_topic_path(self, mocked_subscriber_client):
        """
        `__init__` method should assign a value to `self.topic_path` by calling
        `SubscriberClient.topic_path`
        """
        topic_path_value = "test-topic-path"
        mocked_subscriber_client.return_value.topic_path.return_value = topic_path_value

        subscriber = Subscriber()
        assert subscriber.topic_path == topic_path_value

    def test_create_subscription(self, mocked_subscriber_client):
        """
        `create_subscription` method should call the `SubscriberClient.create_subscription` method
        to create a subscription on pub/sub using `self.subscription_path` and `self.topic_path` as
        part of the request.
        """
        subscriber = Subscriber()
        subscriber.create_subscription()

        # Check the right client method was called
        mocked_subscriber_client.return_value.create_subscription.assert_called_once()

    def test_delete_subscription(self, mocked_subscriber_client):
        """
        `delete_subscription` method should call the `SubscriberClient.delete_subscription` method
        to delete a subscription on pub/sub using `self.subscription_path` as part of the request.
        """
        subscriber = Subscriber()
        subscriber.delete_subscription()

        # Check the right client method was called
        mocked_subscriber_client.return_value.delete_subscription.assert_called_once()

    def test_pull_messages_and_acknowledge_calls_client_pull(self, mocked_subscriber_client):
        """
        `pull_messages_and_acknowledge` method should call the `SubscriberClient.pull` method
        to fetch messages from `self.subscription_path` on pub/sub.
        """

        subscriber = Subscriber()
        subscriber.pull_messages_and_acknowledge()

        # Check the right client method was called
        mocked_subscriber_client.return_value.pull.assert_called_once()

    def test_pull_messages_and_acknowledge_returns_empty_list_if_pull_returns_no_messages(self, mocked_subscriber_client):
        """
        `pull_messages_and_acknowledge` method should return an empty list if
        `SubscriberClient.pull` method returns no messages from `self.subscription_path` on
        pub/sub.
        """
        # Configure the `mocked_subscriber_client` `pull` method to return an empty `PullResponse`
        mocked_pull_response = Mock(spec=PullResponse)
        mocked_pull_response.received_messages = []
        mocked_subscriber_client.return_value.pull.return_value = mocked_pull_response

        subscriber = Subscriber()
        messages = subscriber.pull_messages_and_acknowledge()

        # Returned messages should be an empty list as `PullResponse` is empty
        assert messages == []

    def test_pull_messages_and_acknowledge_returns_valid_messages(self, mocked_subscriber_client):
        """
        `pull_messages_and_acknowledge` method should return a list of messages if
        `SubscriberClient.pull` method returns valid messages from `self.subscription_path` on
        pub/sub.
        """

        # Configure `mocked_subscriber_client.pull` to return representative `PullResponse`
        mocked_pubsub_message = Mock(spec=PubsubMessage)
        mocked_pubsub_message.data = self.message_data
        mocked_received_message = Mock(spec=ReceivedMessage)
        mocked_received_message.message = mocked_pubsub_message
        mocked_received_message.ack_id = 1

        mocked_pull_response = Mock(spec=PullResponse)
        mocked_pull_response.received_messages = [mocked_received_message]

        mocked_subscriber_client.return_value.pull.return_value = mocked_pull_response

        subscriber = Subscriber()
        messages = subscriber.pull_messages_and_acknowledge()

        # Returned messages should be a list of message data
        assert messages == [self.message_data]

    def test_pull_messages_and_acknowledge_acknowledges_messages(self, mocked_subscriber_client):
        """
        `pull_messages_and_acknowledge` method should call the `SubscriberClient.acknowledge` method
        to acknowledge received messages if `SubscriberClient.pull` method returns valid messages from
        `self.subscription_path` on pub/sub.
        """

        # Configure `mocked_subscriber_client.pull` to return representative `PullResponse`
        mocked_pubsub_message = Mock(spec=PubsubMessage)
        mocked_pubsub_message.data = self.message_data
        mocked_received_message = Mock(spec=ReceivedMessage)
        mocked_received_message.message = mocked_pubsub_message
        mocked_received_message.ack_id = 1

        mocked_pull_response = Mock(spec=PullResponse)
        mocked_pull_response.received_messages = [mocked_received_message]

        mocked_subscriber_client.return_value.pull.return_value = mocked_pull_response

        subscriber = Subscriber()
        subscriber.pull_messages_and_acknowledge()

        # Check the right client method was called
        mocked_subscriber_client.return_value.acknowledge.assert_called_once()

    def test_subscription_exists_calls_get_subscription(self, mocked_subscriber_client):
        """
        `subscription_exists` method should call the `SubscriberClient.get_subscription` method
        to check whether a subscription exists at the `self.subscription_path` on pub/sub.
        """
        subscriber = Subscriber()
        subscriber.subscription_exists()

        # Check the right client method was called
        mocked_subscriber_client.return_value.get_subscription.assert_called_once()

    def test_subscription_exists_returns_true_if_subscription_exists(self, mocked_subscriber_client):
        """
        `subscription_exists` method should call the `SubscriberClient.get_subscription` method
        to check whether a subscription exists at the `self.subscription_path` on pub/sub. If the
        method returns successfully, the subscription exists and `subscription_exists` should return
        `True`
        """
        subscriber = Subscriber()
        subscription_exists = subscriber.subscription_exists()

        assert subscription_exists is True

    def test_subscription_exists_returns_false_if_exception_raised(self, mocked_subscriber_client):
        """
        `subscription_exists` method should call the `SubscriberClient.get_subscription` method
        to check whether a subscription exists at the `self.subscription_path` on pub/sub. If the
        method raises an exception, the subscription does not exist and `subscription_exists`
        should return `False`
        """
        # Configure mocked `client.get_subscription` to side effect raise exception, which is what
        # happens if a valid subscription is not found
        mocked_subscriber_client.return_value.get_subscription.side_effect = Exception()

        subscriber = Subscriber()
        subscription_exists = subscriber.subscription_exists()

        assert subscription_exists is False
