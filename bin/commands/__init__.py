"""Shell scripts available after installing the project."""
import enum
import logging
import os
import pathlib
import typer

import coloredlogs
import verboselogs
import yaml
from networkx import DiGraph
from networkx.algorithms.cycles import find_cycle
from networkx.exception import NetworkXNoCycle

# Discover our component directories
_components_path = pathlib.Path("components")
Component = enum.Enum(
    "Component",
    {item: item for item in os.listdir(_components_path) if os.path.isdir(_components_path / item)},
    type=str,
)
"""
The project components.
:autoapiskip:
"""

# Discover the logging levels installed by verboselogs
LogLevel = enum.Enum(
    "LogLevel",
    {
        name: name
        for name in sorted(logging._nameToLevel, key=lambda name: logging._nameToLevel[name])
    },
    type=str,
)
"""
The available logging levels.
:autoapiskip:
"""


def install_coloredlogs(log_level: str):
    """
    Setup our enhanced logging functionality.

    :param log_level: The log level to use for the duration of the command.
    """
    verboselogs.install()
    coloredlogs.install(
        level=log_level,
        fmt="%(levelname)-8s %(message)s",
        level_styles=dict(
            spam=dict(color="green", faint=True),
            debug=dict(color="black", bold=True),
            verbose=dict(color="blue"),
            info=dict(color="white"),
            notice=dict(color="magenta"),
            warning=dict(color="yellow"),
            success=dict(color="green", bold=True),
            error=dict(color="red"),
            critical=dict(color="red", bold=True),
        ),
        field_styles=dict(
            asctime=dict(color="green"),
            hostname=dict(color="magenta"),
            levelname=dict(color="white"),
            name=dict(color="white", bold=True),
            programname=dict(color="cyan"),
            username=dict(color="yellow"),
        ),
    )


def get_component_graph() -> DiGraph:
    """
    Get the dependency graph for our components.

    This reads the ``component.yaml`` file for each component to determine dependencies.

    :return: The dependency graph.
    """
    # Create the graph
    components = DiGraph()
    components.add_nodes_from(Component)
    for component in Component:
        component_yaml = get_component_config(component)
        components.add_edges_from(
            (Component[dependency], component)
            for dependency in component_yaml.get("dependencies", [])
        )

    # Confirm that no cycles are present
    try:
        cycles = find_cycle(components)
    except NetworkXNoCycle:
        return components
    else:
        raise RuntimeError("Cycles found in component dependency graph", cycles)


def get_component_config(component: Component) -> dict:
    """
    Read the contents of the component's component.yaml yaml file.

    :param component: The component whose component.yaml you wish to retrieve.
    :return: The config contents or the empty dictionary if it was not present.
    """
    try:
        with open(
            pathlib.Path("components") / component.value / "component.yaml"
        ) as component_yaml_file:
            return yaml.safe_load(component_yaml_file)
    except FileNotFoundError:
        return {}
