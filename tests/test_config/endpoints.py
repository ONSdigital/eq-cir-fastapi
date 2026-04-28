from typing import TypedDict

# External use endpoints
# 2 versions of get metadata endpoints
GET_CI_METADATA: str = "get_ci_metadata"
GET_CI_METADATA_V1: str = "get_ci_metadata_v1"
# 2 versions of get schema endpoints
GET_CI_SCHEMA: str = "get_ci_schema"
GET_CI_SCHEMA_V1: str = "get_ci_schema_v1"

GET_CI_VALIDATOR_METADATA: str = "get_ci_validator_metadata"
POST_CI: str = "post_ci"
PUT_VALIDATOR_VERSION: str = "put_validator_version"

# Internal use endpoints
DELETE_CI: str = "delete_ci"
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

ENDPOINTS_DEPRECATED: dict[str, EndpointConfig] = {
    DELETE_CI: {
        "url": "/v1/dev/teardown",
        "method": "DELETE",
    },
    GET_CI_METADATA: {
        "url": "/v2/ci_metadata",
        "method": "GET",
    },
    GET_CI_METADATA_V1: {
        "url": "/v1/ci_metadata",
        "method": "GET",
    },
    GET_CI_SCHEMA: {
        "url": "/v2/retrieve_collection_instrument",
        "method": "GET",
    },
    GET_CI_SCHEMA_V1: {
        "url": "/v1/retrieve_collection_instrument",
        "method": "GET",
    },
    GET_CI_VALIDATOR_METADATA: {
        "url": "/v1/ci_validator_metadata",
        "method": "GET",
    },
    POST_CI: {
        "url": "/v3/publish_collection_instrument",
        "method": "POST",
    },
    PUT_VALIDATOR_VERSION: {
        "url": "/v1/update_validator_version",
        "method": "PUT",
    },
    GET_STATUS: {
        "url": "/status",
        "method": "GET",
    }
}
