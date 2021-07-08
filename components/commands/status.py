"""A command to return the current status of this service."""
import asyncio
import logging
import os

from aiohttp import ClientConnectionError, ClientSession
from aredis.exceptions import RedisError
from elasticsearch import ElasticsearchException

from shared.elasticsearch_util.elasticsearch_connection import NoElasticSearchBackend, get_es_health
from shared.redis_util.redis_connection import NoRedisBackend, ping_redis

logger = logging.getLogger(__name__)


def parse_args(sub_parser):
    """Parse arguments for the "status" command."""
    subparser = sub_parser.add_parser("status", help="Report on the status of the application")
    # register the function to be executed when command "status" is called
    subparser.set_defaults(func=print_status)


def print_status(_):
    """Print the status of the service's pods."""
    logger.debug("Printing server status...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(print_api_status())
    loop.run_until_complete(print_redis_status())
    print_elasticsearch_status()


async def print_api_status():
    """Log the status of the api pod."""
    logger.debug("Pinging API server...")
    host = os.environ["FAST_API_PROTOTYPE_API_SERVICE_HOST"]
    port = os.environ["FAST_API_PROTOTYPE_API_SERVICE_PORT"]
    url = f"http://{host}:{port}/ping"

    try:
        async with ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    logger.success("API server ping successful")
                else:
                    logger.error("API server ping failed with status code %s", response.status)
                await response.text()
    except ClientConnectionError:
        logger.exception("Failed to connect to API server")


async def print_redis_status():
    """Log the status of the redis backend."""
    # TODO have this ping external redis when that gets added
    logger.debug("Pinging redis...")
    try:
        logger.success("Redis ping: %s", await ping_redis())
    except NoRedisBackend:
        logger.notice("Redis creation flag set to false; no connection available at this time")
    except RedisError:
        logger.exception("Failed to query redis server")


def print_elasticsearch_status():
    """Log the status of the elasticsearch backend."""
    logger.debug("Getting elasticsearch health...")
    try:
        status = get_es_health()
        logger.success("Elasticsearch health: %s", status)
    except NoElasticSearchBackend:
        logger.notice(
            "Elasticsearch creation flag set to false; no connection available at this time"
        )
    except ElasticsearchException:
        logger.exception("Failed to query elasticsearch server")
