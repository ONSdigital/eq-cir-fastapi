from fastapi.openapi.utils import get_openapi
import yaml

from app.main import app

OUTPUT_FILENAME = "openapi.yaml"


# Writes the FastApi schema to an output yaml file
with open(OUTPUT_FILENAME, 'w+') as f:
    yaml.dump(get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    ), f)
