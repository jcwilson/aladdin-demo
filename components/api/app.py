import logging
import math
import os

from ddtrace_asgi.middleware import TraceMiddleware
from elasticsearch_util.elasticsearch_connection import connection as elasticsearch
from fastapi import FastAPI
from redis_util.redis_connection import connection as redis


logger = logging.getLogger()


def create_app():
    app = FastAPI(openapi_url="/_api/openapi.json", docs_url="/_api/docs", redoc_url="/_api/redoc")

    # The app is being run with ddtrace, so install the necessary middleware
    if os.environ["APM_ENABLED"] == "true":
        logger.info("Datadog APM enabled; installing middleware")
        app.add_middleware(TraceMiddleware, service=os.environ["DATADOG_SERVICE_NAME"])

    @app.get("/ping")
    def read_ping():
        return {}

    @app.get("/app")
    def read_base_message():
        return {"message": "I can show you the world"}

    @app.get("/app/busy")
    def read_busy_message():
        # A computationally intensive resource to demonstrate autoscaling
        n = 0.0001
        for i in range(1000000):
            n += math.sqrt(n)
        return {"message": "busy busy..."}

    if redis:
        logger.info("Redis backend created; enabling redis endpoints")

        @app.get("/app/redis")
        async def read_redis_message():
            return {"message": await redis.get("msg")}

    if elasticsearch:
        logger.info("Elasticsearch backend created; enabling elasticsearch endpoints")

        @app.get("/app/elasticsearch")
        def read_elasticsearch_message():
            data = elasticsearch.get(index="messages", doc_type="song", id=1)
            return {"message": data["_source"]}

    return app
