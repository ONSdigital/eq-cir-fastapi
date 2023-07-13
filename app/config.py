from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    CI_FIRESTORE_COLLECTION_NAME: str = "ons-collection-instruments"
    CI_STORAGE_BUCKET_NAME: str
    DEFAULT_HOSTNAME: str = "only required for integration tests"
    OAUTH_CLIENT_ID: str = "only required for integration tests"
    PROJECT_ID: str
    PUBSUB_EMULATOR_HOST: str = "http://localhost:8085"
    STORAGE_EMULATOR_HOST: str = "http://localhost:9024"
    SUBSCRIPTION_ID: str = "ons-cir-publish-events-subscription-cir"
    TOPIC_ID: str = "ons-cir-publish-events"
