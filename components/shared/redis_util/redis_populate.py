"""
Functionality to populate the redis cluster with some initial data.

This can imported to get the populate() function, or run directly as a script.
"""
import asyncio
import logging

from redis_connection import CONNECTION


def main():
    """Set up the logging config and populate the cluster."""
    logging.basicConfig(
        format="%(levelname)-8s %(name)s(%(lineno)d) %(message)s", level=logging.INFO
    )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(populate(CONNECTION))


async def populate(connection):
    """Create a single boilerplate record in the elasticsearch cluster."""
    logging.info("Populating redis...")
    await connection.set("msg", "I can show you the world from Redis")
    logging.info("Redis populated")


if __name__ == "__main__":
    main()
