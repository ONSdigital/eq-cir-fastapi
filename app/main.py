from fastapi import FastAPI

from app.config import Settings

app = FastAPI()
settings = Settings()


@app.get("/")
async def read_root():
    return settings.model_dump()
