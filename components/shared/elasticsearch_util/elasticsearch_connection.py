"""Provides a connection to the elasticsearch backend and some basic convenience functionality."""
import os

from elasticsearch import Elasticsearch


class NoElasticSearchBackend(Exception):
    """Raised if connection does not exist because we didn't create the backend service."""


# TODO: Remove once external (aws) script is in place
CONNECTION = (
    Elasticsearch(hosts=[os.environ["ELASTICSEARCH_HOST"]])
    if os.environ["ELASTICSEARCH_CREATE"] == "true"
    else None
)


def get_es_health() -> dict:
    """Get the elasticsearch cluster health report."""
    if not CONNECTION:
        raise NoElasticSearchBackend
    return CONNECTION.cluster.health()
