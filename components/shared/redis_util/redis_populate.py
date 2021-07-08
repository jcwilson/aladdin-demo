"""Functionality to populate the redis cluster with some initial data."""
import logging

from aredis import StrictRedis

logger = logging.getLogger(__name__)


async def populate(connection: StrictRedis):
    """Create a single boilerplate record in the elasticsearch cluster."""
    logger.info("Populating redis...")
    await connection.set("msg", "I can show you the world from Redis")
    logger.info("Redis populated")
