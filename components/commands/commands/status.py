import logging

import asyncio
import os

import aiohttp
from aredis.exceptions import RedisError

from shared.elasticsearch import ElasticsearchException
from shared.elasticsearch_util.elasticsearch_connection import NoElasticSearchBackend, get_es_health
from shared.redis_util.redis_connection import NoRedisBackend, ping_redis


logger = logging.getLogger(__name__)


def parse_args(sub_parser):
    subparser = sub_parser.add_parser("status", help="Report on the status of the application")
    # register the function to be executed when command "status" is called
    subparser.set_defaults(func=print_status)


def print_status(arg):
    """ Prints the status of the aladdin-demo pod and the redis pod """
    logger.debug("Printing server status...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(print_aladdin_demo_server_status())
    loop.run_until_complete(print_redis_status())
    print_elasticsearch_status()


async def print_aladdin_demo_server_status():
    logger.debug("Pinging API server...")
    host = os.environ["FAST_API_PROTOTYPE_API_SERVICE_HOST"]
    port = os.environ["FAST_API_PROTOTYPE_API_SERVICE_PORT"]
    url = f"http://{host}:{port}/ping"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    logger.info("API server ping successful")
                else:
                    logger.info("API server ping failed with status code %s", response.status)
                await response.text()
    except aiohttp.ClientConnectionError:
        logger.exception("Failed to connect to API server")


async def print_redis_status():
    # TODO have this ping external redis when that gets added
    logger.debug("Pinging redis...")
    try:
        status = await ping_redis()
        logger.info("Redis ping successful: %s", status)
    except NoRedisBackend:
        logger.warning("Redis creation flag set to false; no connection available at this time")
    except RedisError:
        logger.exception("Failed to query redis server")


def print_elasticsearch_status():
    logger.debug("Getting elasticsearch health...")
    try:
        status = get_es_health()
        logger.info("Elasticsearch health retrieved: %s", status)
    except NoElasticSearchBackend:
        logger.warning(
            "Elasticsearch creation flag set to false; no connection available at this time"
        )
    except ElasticsearchException:
        logger.exception("Failed to query elasticsearch server")
