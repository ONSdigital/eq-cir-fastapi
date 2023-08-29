import logging

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    CI_FIRESTORE_COLLECTION_NAME: str = "ons-collection-instruments"
    CI_STORAGE_BUCKET_NAME: str = "ons-cir-dev"
    DEFAULT_HOSTNAME: str = "only required for integration tests"
    OAUTH_CLIENT_ID: str = "only required for integration tests"
    LOG_LEVEL: str = "INFO"
    PROJECT_ID: str = "ons-cir-dev"
    PUBLISHED_AT_FORMAT: str = "%Y-%m-%dT%H:%M:%S.%fZ"
    PUBSUB_EMULATOR_HOST: str = "only required for development environment"
    STORAGE_EMULATOR_HOST: str = "only required for development environment"
    SUBSCRIPTION_ID: str = "ons-cir-publish-events-subscription-cir"
    TOPIC_ID: str = "ons-cir-publish-ci"
    URL_SCHEME: str = "only required for integration tests"


settings = Settings()


logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
