import datetime
import os

import pytest
from gcp_storage_emulator.server import create_server
from google.cloud import pubsub_v1
from mockfirestore import MockFirestore

from app.config import Settings, logging

logger = logging.getLogger(__name__)
mock_publish_date = datetime.datetime(2023, 4, 20, 12, 0, 0, 0)
settings = Settings()


@pytest.fixture(scope="session")
def setup_mock_firestore():
    logger.debug("***setup_mock_firestore")
    firestore_client = MockFirestore()

    return firestore_client


@pytest.fixture(autouse=True)
def mock_firestore_collection(mocker, setup_mock_firestore):
    logger.debug("***mock_firestore_collection")
    # mock firebase client
    mocker.patch("app.repositories.firebase.firebase_loader.firebase_loader.get_client", return_value=setup_mock_firestore)
    # mock firestore ci collection
    collection = setup_mock_firestore.collection(settings.CI_FIRESTORE_COLLECTION_NAME)
    mocker.patch("app.repositories.firebase.firebase_loader.firebase_loader.get_ci_collection", return_value=collection)
    # use ci collection
    yield collection
    setup_mock_firestore.reset()


@pytest.fixture(scope="session")
def setup_mock_storage():
    logger.debug("local storage starting")
    server = create_server(
        "localhost",
        9023,
        in_memory=True,
        default_bucket="ons-cir-schemas",
    )
    os.environ.setdefault("STORAGE_EMULATOR_HOST", "http://localhost:9023")
    server.start()
    logger.info("local storage started")
    yield server
    logger.debug("local storage stopping")
    server.stop()
    logger.info("local storage stopped")


@pytest.fixture
def patch_datetime_now(monkeypatch):
    class mydatetime:
        @classmethod
        def utcnow(cls):
            return mock_publish_date

    monkeypatch.setattr(
        datetime,
        "datetime",
        mydatetime,
    )


@pytest.fixture(autouse=True)
def mock_datetime(mocker):
    mocker.patch("app.services.datetime_service.DatetimeService.get_current_date_and_time", return_value=mock_publish_date)


@pytest.fixture(scope="session")
def setup_pubsub_emulator():
    # Set the environment variable for the Pub/Sub emulator host and port
    os.environ.setdefault("PUBSUB_EMULATOR_HOST", "http://localhost:8085")

    # Create a Pub/Sub publisher client
    publisher = pubsub_v1.PublisherClient()

    # Create the topic if it doesn't exist
    topic_id = "post-ci"  # Replace with your topic ID
    topic_path = f"projects/{publisher.project}/topics/{topic_id}"

    try:
        publisher.create_topic(request={"name": topic_path})
    except Exception as e:
        pytest.fail(f"Failed to create Pub/Sub topic: {e}")

    yield
