"""Functionality to populate the elasticsearch cluster with some initial data."""
import logging

from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)


def populate(connection: Elasticsearch):
    """Create a single boilerplate record in the elasticsearch cluster."""
    logger.info("Populating elasticsearch...")
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
    logger.info("Elasticsearch populated")
