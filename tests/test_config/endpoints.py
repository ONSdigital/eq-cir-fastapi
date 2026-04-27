from typing import TypedDict

DELETE_CI: str = "delete_ci"
GET_CI_METADATA: str = "get_ci_metadata"
GET_CI_METADATA_V1: str = "get_ci_metadata_v1"
GET_CI_SCHEMA: str = "get_ci_schema"
GET_CI_SCHEMA_V1: str = "get_ci_schema_v1"
GET_CI_VALIDATOR_METADATA: str = "get_ci_validator_metadata"
POST_CI: str = "post_ci"
PUT_VALIDATOR_VERSION: str = "put_validator_version"
GET_STATUS: str = "get_status"


class EndpointConfig(TypedDict):
    url: str
    method: str


ENDPOINTS: dict[str, EndpointConfig] = {
    DELETE_CI: {
        "url": "/v1/collection-instruments",
        "method": "DELETE",
    },
    GET_CI_METADATA: {
        "url": "/v2/collection-instruments/metadata",
        "method": "GET",
    },
    GET_CI_METADATA_V1: {
        "url": "/v1/collection-instruments/metadata",
        "method": "GET",
    },
    GET_CI_SCHEMA: {
        "url": "/v2/collection-instruments/schema",
        "method": "GET",
    },
    GET_CI_SCHEMA_V1: {
        "url": "/v1/collection-instruments/schema",
        "method": "GET",
    },
    GET_CI_VALIDATOR_METADATA: {
        "url": "/v1/collection-instruments/validator-metadata",
        "method": "GET",
    },
    POST_CI: {
        "url": "/v3/collection-instruments",
        "method": "POST",
    },
    PUT_VALIDATOR_VERSION: {
        "url": "/v1/collection-instruments/validator-version",
        "method": "PUT",
    },
    GET_STATUS: {
        "url": "/status",
        "method": "GET",
    }
}