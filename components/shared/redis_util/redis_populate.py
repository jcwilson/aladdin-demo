import asyncio
import logging

from redis_connection import connection


def main():
    logging.basicConfig(
        format="%(levelname)-8s %(name)s(%(lineno)d) %(message)s", level=logging.INFO
    )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(populate(connection))


async def populate(connection):
    logging.info("Populating redis...")
    await connection.set("msg", "I can show you the world from Redis")
    logging.info("Redis populated")


if __name__ == "__main__":
    main()
