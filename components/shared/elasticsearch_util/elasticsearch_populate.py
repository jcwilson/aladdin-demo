"""
Functionality to populate the elasticsearch cluster with some initial data.

This can imported to get the populate() function, or run directly as a script.
"""
import logging

from elasticsearch_connection import CONNECTION


def main():
    """Set up the logging config and populate the cluster."""
    logging.basicConfig(
        format="%(levelname)-8s %(name)s(%(lineno)d) %(message)s", level=logging.INFO
    )

    populate(CONNECTION)


def populate(connection):
    """Create a single boilerplate record in the elasticsearch cluster."""
    logging.info("Populating elasticsearch...")
    connection.index(
        index="messages",
        doc_type="song",
        id=1,
        body={
            "author": "Aladdin",
            "song": "A Whole New World",
            "lyrics": ["I can show you the world"],
            "awesomeness": 42,
        },
    )
    logging.info("Populated elasticsearch")


if __name__ == "__main__":
    main()
