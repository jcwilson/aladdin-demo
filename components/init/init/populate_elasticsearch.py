"""A poetry script to populate the elasticsearch cluster with some initial data."""
import logging

from shared.elasticsearch_util.elasticsearch_connection import CONNECTION
from shared.elasticsearch_util.elasticsearch_populate import populate


def main():
    """Populate the elasticsearch cluster with some initial data."""
    logging.basicConfig(
        format="%(levelname)-8s %(name)s(%(lineno)d) %(message)s", level=logging.INFO
    )

    populate(CONNECTION)
