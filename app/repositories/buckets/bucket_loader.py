from typing import Any

from google.cloud import exceptions, storage

from app.config import logging, settings
from app.exception.exceptions import ExceptionBucketNotFound

logger = logging.getLogger(__name__)


class BucketLoader:
    ci_schema_bucket: storage.Bucket | None = None
    __storage_client: storage.Client

    def __init__(self, storage_client: storage.Client) -> None:
        self.__storage_client = storage_client

        if settings.CONF == "unit":
            return

        self.ci_schema_bucket = self._initialise_bucket(settings.CI_STORAGE_BUCKET_NAME)

    def get_ci_schema_bucket(self) -> storage.Bucket:
        """
        Get the ci schema bucket from Google cloud
        """
        return self.ci_schema_bucket

    def _create_bucket(self, bucket_name: str) -> storage.Bucket:
        """
        Create a bucket in Google cloud storage

        Parameters:
        bucket_name (str): The bucket name to create
        """
        try:
            bucket = self.__storage_client.create_bucket(
                bucket_name,
                project=settings.PROJECT_ID,
            )

            logger.debug(f"Bucket created: {bucket_name}")

            return bucket

        except exceptions.Conflict as exc:
            logger.debug("Bucket already exists")

            raise Exception("Bucket already exists") from exc

    def _initialise_bucket(self, bucket_name) -> Any | None:
        """
        Connect to google cloud storage client using PROJECT_ID
        If bucket does not exists, then create the bucket
        Else connect to the bucket

        Parameters:
        bucket_name (str): The bucket name
        """
        try:
            bucket = self.__storage_client.get_bucket(
                bucket_name,
            )
        except exceptions.NotFound as exc:
            logger.debug("Error getting bucket")

            if settings.CONF != "local-docker":
                raise ExceptionBucketNotFound from exc

            # If bucket does not exist, create it
            bucket = self._create_bucket(bucket_name)

        return bucket


client = storage.Client(project=settings.PROJECT_ID)
bucket_loader = BucketLoader(client)
