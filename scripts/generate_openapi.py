import os

import yaml
from fastapi.openapi.utils import get_openapi

from app.main import app

OUTPUT_PATH = os.path.join(os.getcwd(), "gateway", "openapi.yaml")


# Writes the FastApi schema to an output yaml file
with open(OUTPUT_PATH, "w+") as f:
    yaml.dump(
        get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        ),
        f,
    )
