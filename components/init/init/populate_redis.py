"""A poetry script to populate the redis cluster with some initial data."""
import asyncio
import logging

from shared.redis_util.redis_connection import CONNECTION
from shared.redis_util.redis_populate import populate


def main():
    """Populate the redis cluster with some initial data."""
    logging.basicConfig(
        format="%(levelname)-8s %(name)s(%(lineno)d) %(message)s", level=logging.INFO
    )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(populate(CONNECTION))
