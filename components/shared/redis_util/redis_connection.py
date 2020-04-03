import os

from aredis import StrictRedis


class NoRedisBackend(Exception):
    """Raised if connection does not exist because we didn't create the backend service"""


# TODO: Remove once external (aws) redis script is in place
connection = (
    StrictRedis(
        host=os.environ["FAST_API_PROTOTYPE_REDIS_SERVICE_HOST"],
        port=os.environ["FAST_API_PROTOTYPE_REDIS_SERVICE_PORT"],
    )
    if os.environ["REDIS_CREATE"] == "true"
    else None
)


async def ping_redis():
    if not connection:
        raise NoRedisBackend
    return await connection.ping()
