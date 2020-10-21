import os

from fastapi import FastAPI

from app.mongo import Mongo
from app.routers.apis import api_router

api_prefix = "/api/v1"

app = FastAPI(
    title="Demo App",
    description="This is a demonstration application.",
    version=os.getenv("API_VERSION"),
    docs_url="/",
    redoc_url=None,
    openapi_url=api_prefix + "/openapi.json"
)


@app.on_event("startup")
async def start_up() -> None:
    """Execute this function before this application starts up.
    """
    await Mongo.connect()
    app.include_router(api_router, prefix=api_prefix)


@app.on_event("shutdown")
async def shut_down() -> None:
    """Execute this function before this application is shutting down.
    """
    await Mongo.disconnect()
