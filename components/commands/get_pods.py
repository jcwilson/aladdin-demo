"""A command to return a list of pods for this service."""
import logging
import os

from kubernetes import client, config

logger = logging.getLogger(__name__)


def parse_args(sub_parser):
    """Parse arguments for the "get-pods" command."""
    subparser = sub_parser.add_parser("get-pods", help="Get all project pods")
    subparser.set_defaults(func=get_pods)


def get_pods(_):
    """Log the list of pods for this service."""
    logger.info("Pods: %s", get_service_pods())


def get_service_pods():
    """Query kubernetes for the list of pods for this service."""
    config.load_incluster_config()
    v1api = client.CoreV1Api()
    res = v1api.list_namespaced_pod(
        namespace=os.environ["NAMESPACE"], label_selector=f"project={os.environ['PROJECT_NAME']}"
    )
    return [r.metadata.name for r in res.items]
