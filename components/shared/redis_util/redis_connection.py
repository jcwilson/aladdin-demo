"""Provides a connection to the redis backend and some basic convenience functionality."""
import os

from aredis import StrictRedis


class NoRedisBackend(Exception):
    """Raised if connection does not exist because we didn't create the backend service."""


# TODO: Remove once external (aws) redis script is in place
CONNECTION = (
    StrictRedis(
        host=os.environ["FAST_API_PROTOTYPE_REDIS_SERVICE_HOST"],
        port=os.environ["FAST_API_PROTOTYPE_REDIS_SERVICE_PORT"],
    )
    if os.environ["REDIS_CREATE"] == "true"
    else None
)
"""The aredis connection object, if available"""


async def ping_redis() -> dict:
    """
    Check to see if redis backend is available.

    :return: The connection ping results
    """
    if not CONNECTION:
        raise NoRedisBackend
    return await CONNECTION.ping()
