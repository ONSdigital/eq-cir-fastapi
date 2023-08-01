import json

from google.cloud import exceptions, storage

from app.config import Settings, logging
from app.models.responses import CiMetadata

__bucket = None
logger = logging.getLogger(__name__)
settings = Settings()


def get_storage_bucket():
    global __bucket
    if not __bucket:
        __storage_client = storage.Client(project=settings.PROJECT_ID)
        try:
            __bucket = __storage_client.get_bucket(
                settings.CI_STORAGE_BUCKET_NAME,
            )
        except exceptions.NotFound:
            __bucket = __storage_client.create_bucket(
                settings.CI_STORAGE_BUCKET_NAME,
            )
    return __bucket


def store_ci_schema(blob_name, schema):
    logger.info("attempting to store schema")
    logger.debug(f"{blob_name} {schema}")

    bucket = get_storage_bucket()
    blob = bucket.blob(blob_name)
    blob.upload_from_string(json.dumps(schema))
    logger.info("success stored: put_schema")


def retrieve_ci_schema(blob_name):
    logger.info("attempting to get schema")
    logger.debug(f"get_schema blob_name: {blob_name}")
    bucket = get_storage_bucket()
    blob = bucket.blob(blob_name)
    if not blob.exists():
        return None
    data = blob.download_as_string()
    logger.debug(f"get_schema data: {data}")
    return json.loads(data)


def delete_ci_schema(ci_schemas: list[CiMetadata]):
    logger.info("attempting to delete schema")
    bucket = get_storage_bucket()
    for schema in ci_schemas:
        blob_name = schema.id
        logger.debug(f"delete_ci_schema: {blob_name}")
        blob = bucket.blob(blob_name)
        blob.delete()
        logger.info(f"success deleted: {blob_name}")
