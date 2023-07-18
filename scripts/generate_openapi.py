import os

from fastapi.openapi.utils import get_openapi
import yaml

from app.main import app

OUTPUT_DIR = "gateway"
OUTPUT_FILENAME = "openapi.yaml"

OUTPUT_PATH = os.path.join(os.getcwd(), OUTPUT_DIR, OUTPUT_FILENAME)


# Writes the FastApi schema to an output yaml file
with open(OUTPUT_PATH, 'w+') as f:
    yaml.dump(get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    ), f)
