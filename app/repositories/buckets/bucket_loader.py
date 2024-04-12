from google.cloud import exceptions, storage

from app.config import settings


class BucketLoader:
    def __init__(self):
        self.ci_schema_bucket = self._initialise_bucket(settings.CI_STORAGE_BUCKET_NAME)

    def get_ci_schema_bucket(self) -> storage.Bucket:
        """
        Get the ci schema bucket from Google cloud
        """
        return self.ci_schema_bucket

    def _initialise_bucket(self, bucket_name) -> storage.Bucket:
        """
        Connect to google cloud storage client using PROJECT_ID
        If bucket does not exists, then create the bucket
        Else connect to the bucket

        Parameters:
        bucket_name (str): The bucket name
        """
        if settings.CONF == "unit":
            return None

        __storage_client = storage.Client(project=settings.PROJECT_ID)
        try:
            bucket = __storage_client.get_bucket(
                bucket_name,
            )
        except exceptions.NotFound:
            bucket = __storage_client.create_bucket(
                bucket_name,
            )

        return bucket


bucket_loader = BucketLoader()
