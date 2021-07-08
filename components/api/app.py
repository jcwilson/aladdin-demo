"""The FastAPI application endpoints."""

import logging
import math
import os

from ddtrace_asgi.middleware import TraceMiddleware
from fastapi import FastAPI

from shared.elasticsearch_util.elasticsearch_connection import (
    CONNECTION as ELASTICSEARCH_CONNECTION,
)
from shared.redis_util.redis_connection import CONNECTION as REDIS_CONNECTION

logger = logging.getLogger()


def create_app():
    """Create the FastAPI application."""
    app = FastAPI(openapi_url="/_api/openapi.json", docs_url="/_api/docs", redoc_url="/_api/redoc")

    # The app is being run with ddtrace, so install the necessary middleware
    if os.environ["APM_ENABLED"] == "true":
        logger.info("Datadog APM enabled; installing middleware")
        app.add_middleware(TraceMiddleware, service=os.environ["DATADOG_SERVICE_NAME"])

    @app.get("/ping")
    def read_ping():  # pylint: disable=unused-variable
        return {}

    @app.get("/app")
    def read_base_message():  # pylint: disable=unused-variable
        return {"message": "I can show you the world"}

    @app.get("/app/busy")
    def read_busy_message():  # pylint: disable=unused-variable
        # A computationally intensive resource to demonstrate autoscaling
        nonce = 0.0001
        for _ in range(1000000):
            nonce += math.sqrt(nonce)
        return {"message": "busy busy..."}

    if REDIS_CONNECTION:
        logger.info("Redis backend created; enabling redis endpoints")

        @app.get("/app/redis")
        async def read_redis_message():  # pylint: disable=unused-variable
            return {"message": await REDIS_CONNECTION.get("msg")}

    if ELASTICSEARCH_CONNECTION:
        logger.info("Elasticsearch backend created; enabling elasticsearch endpoints")

        @app.get("/app/elasticsearch")
        def read_elasticsearch_message():  # pylint: disable=unused-variable
            data = ELASTICSEARCH_CONNECTION.get(index="messages", doc_type="song", id=1)
            return {"message": data["_source"]}

    return app
