import os

from elasticsearch import Elasticsearch


class NoElasticSearchBackend(Exception):
    """Raised if connection does not exist because we didn't create the backend service"""


# TODO: Remove once external (aws) script is in place
connection = (
    Elasticsearch(hosts=[os.environ["ELASTICSEARCH_HOST"]])
    if os.environ["ELASTICSEARCH_CREATE"] == "true"
    else None
)


def get_es_health():
    if not connection:
        raise NoElasticSearchBackend
    return connection.cluster.health()
