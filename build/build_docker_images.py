#!/usr/bin/env python3

import atexit
import collections
import functools
import json
import logging
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import textwrap
import typing
import yaml

import coloredlogs
import verboselogs


class Undefined:
    def __bool__(self):
        return False

    def __str__(self):
        raise NotImplementedError


UNDEFINED = Undefined()


class ConfigurationException(Exception):
    """Raised if there is an error in the component.yaml."""


class UserInfo(collections.namedtuple("UserInfo", ["name", "group", "home"])):
    def __bool__(self):
        return all(self)

    @property
    def chown(self):
        return f"{self.name}:{self.group}"


class ComponentConfig:
    """The representation of the component.yaml."""

    def __init__(self, data: dict):
        self._data = data
        self.validate()

    def validate(self):
        """Raises a ConfigurationException if the values are invalid."""

    def get(self, path: str, default: typing.Any = UNDEFINED):
        """Perform a dot-delimited lookup on the provided path name."""
        return functools.reduce(
            lambda d, key: d.get(key, default) if isinstance(d, dict) else default,
            path.split("."),
            self._data,
        )

    def should_build_for_cluster(self, cluster: str):
        return self.clusters is UNDEFINED or cluster in self.clusters

    @property
    def version(self):
        return self.get("meta.version", 1)

    @property
    def language_name(self):
        name = self.get("language.name")
        return name.lower() if name else UNDEFINED

    @property
    def language_version(self):
        version = self.get("language.version")
        return str(version) if version else UNDEFINED

    @property
    def clusters(self):
        return self.get("clusters")

    @property
    def image_base(self):
        return self.get("image.base")

    @property
    def image_aladdinize(self):
        return self.get("image.aladdinize")

    @property
    def image_add_poetry(self):
        return self.get("image.add_poetry")

    @property
    def dependencies(self):
        return self.get("dependencies")

    @property
    def user_info(self):
        return UserInfo(
            name=self.get("user.name"), group=self.get("user.group"), home=self.get("user.home")
        )


class BuildInfo(
    collections.namedtuple(
        "BuildInfo",
        [
            "project",
            "to_publish",
            "component",
            "config",
            "hash",
            "default_language_version",
            "poetry_version",
        ],
    )
):
    """
    A wrapper around the component config and some other high-level info to make parameterizing
    the build process a bit simpler. The build functions should use this rather than directly
    accessing the config.
    """

    def set_user_info(self, user_info: UserInfo):
        self._user_info = user_info

    def set_language_version(self, version: str):
        self._language_version = version

    @property
    def language_name(self):
        return self.config.language_name

    @property
    def language_version(self):
        return getattr(
            self, "_language_version", self.config.language_version or self.default_language_version
        )

    @property
    def has_python_dependencies(self):
        component_path = pathlib.Path("components") / self.component
        pyproject_path = component_path / "pyproject.toml"
        lock_path = component_path / "poetry.lock"
        return pyproject_path.exists() and lock_path.exists()

    @property
    def tag(self):
        return f"{self.project}-{self.component}:{self.hash}"

    @property
    def dev(self):
        return self.hash == "local"

    @property
    def poetry_no_dev(self):
        return "" if self.dev else "--no-dev"

    @property
    def python_optimize(self):
        return "" if self.dev else "-O"

    @property
    def base_image(self):
        return self.config.image_base or f"python:{self.language_version}-slim"

    @property
    def builder_image(self):
        return f"python:{self._language_version}-slim"

    @property
    def aladdinize(self):
        return (
            self.config.image_aladdinize if self.config.image_aladdinize is not UNDEFINED else True
        )

    @property
    def add_poetry(self):
        return self.hash == "local" and (
            self.config.image_add_poetry if self.config.image_add_poetry is not UNDEFINED else True
        )

    @property
    def specialized_dockerfile(self):
        path = pathlib.Path("components") / self.component / "Dockerfile"
        return path.as_posix() if path.exists() else None

    @property
    def user_info(self):
        return getattr(self, "_user_info", self.config.user_info)

    @property
    def dependencies(self):
        return self.config.dependencies or []


class DockerIgnore:
    """
    A class to be used to temporarily modify the singleton .dockerignore file for the various
    build steps we undertake in the component building process. This is the core magic that allows
    us to place all of our code under a single docker context but judiciously decide which parts to
    send to each build step.
    """

    def __init__(self, ignore_file: typing.IO, original_file_name: str):
        self._ignore_file = ignore_file
        with open(original_file_name) as original_file:
            self._original_content = original_file.read()

        self.write("")
        self.write("### Ephemeral modifications ###")
        self.write("# Specific instructions")

    def ignore_all(self):
        self.ignore("**")

    def ignore_defaults(self):
        """Copy the contents of the original .DockerIgnore file into the temporary one."""
        self.write("")
        self.write("### Original content ###")
        self.write(self._original_content)

    def ignore(self, entry: str):
        self.write(entry)

    def include(self, entry: str):
        self.write(f"!{entry}")

    def write(self, entry: str):
        self._ignore_file.write(f"{entry}\n")
        self._ignore_file.flush()


def dockerignore(mode: str):
    """
    A decorator to allow the decorated function to manipulate the .dockerignore file for a build.

    It provides the ignore_file argument to the decorated function with the DockerIgnore instance
    wrapping the already opened file.

    :param mode: The file mode string to use to open the .dockerignore file
    :return: The decorated function
    """
    original_path = pathlib.Path("components") / ".dockerignore"

    def decorator(func: typing.Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with tempfile.NamedTemporaryFile() as tmpfile:
                shutil.copyfile(original_path, tmpfile.name)
                atexit.register(shutil.copyfile, tmpfile.name, original_path)
                try:
                    with open(original_path, mode) as file:
                        return func(ignore_file=DockerIgnore(file, tmpfile.name), *args, **kwargs)
                finally:
                    shutil.copyfile(tmpfile.name, original_path)
                    atexit.unregister(shutil.copyfile)

        return wrapper

    return decorator


def build(
    lamp: dict,
    hash: str,
    components: typing.List = None,
    default_python_version: str = "3.8",
    poetry_version: str = "1.0.5",
):
    """
    Build each component for the project.

    If components is empty, this will assume each directory in the components/ directory is a
    component and will build each of them.
    """
    if not components:
        # Just build everything
        path = pathlib.Path("components")
        components = [item for item in os.listdir(path) if os.path.isdir(path / item)]

    for component in components:
        # Read the component.yaml file
        component_config = create_component_config(component)

        # This provides a secondary check against accidentally publishing and/or deploying
        # a dev component to a hosted cluster.
        if component_config.should_build_for_cluster(os.environ["CLUSTER_NAME"]):

            # We currently assume every component is python.
            # This assumption could conceivably be configured in the lamp.json file for
            # language-homogenous projects.
            language = component_config.language_name or "python"

            if language == "python":
                build_info = BuildInfo(
                    project=lamp["name"],
                    to_publish=lamp["docker_images"],
                    component=component,
                    config=component_config,
                    hash=hash,
                    # TODO: Handle these in a better manner when adding support for other languages
                    default_language_version=default_python_version,
                    poetry_version=poetry_version,
                )

                language_version = build_info.language_version
                if language_version.startswith("3"):
                    # We only support python 3 components at the moment
                    build_python_component_image(build_info)
                else:
                    raise ValueError(
                        f"Unsupported python version for {component} component: {language_version}"
                    )
            else:
                raise ValueError(
                    f"Unsupported language for {component} component: {language}:{language_version}"
                )
        else:
            logger.notice(
                "Not building %s component due to '%s' not being in the cluster whitelist",
                component,
                os.environ["CLUSTER_NAME"],
            )
            build_empty_image(build_info)
    else:
        logger.success("Built images for components: %s", ", ".join(components))


def create_component_config(component: str) -> ComponentConfig:
    """
    Read the component's component.yaml file into a ComponentConfig object.

    If the component does not provide a component.yaml file, this returns an empty ComponentConfig.
    """
    try:
        with open(pathlib.Path("components") / component / "component.yaml") as file:
            return ComponentConfig(yaml.safe_load(file))
    except ConfigurationException:
        raise
    except Exception:
        return ComponentConfig({})


def build_empty_image(build_info: BuildInfo):
    """
    Build an image that simply displays a message explaining why the expected image wasn't built.
    """
    _docker_build(
        dockerfile="build/python/echo-message.dockerfile",
        tag=build_info.tag,
        buildargs=dict(
            MESSAGE=(
                textwrap.dedent(
                    f"""
                    This image was published but is not meant to be run in this environment.

                    If you're seeing this, you probably need to add this cluster to the
                    clusters list in the components/{build_info.component}/component.yaml file.
                    """
                )
            )
        ),
    )


def build_python_component_image(build_info: BuildInfo):
    """
    Build the component.

    This builds the component image according to the component.yaml configuration. It begins by
    building a base image and then adding to it things like the poetry tool and any component
    dependency assets.
    """
    try:
        logger.notice("Building image for component: %s", build_info.component)
        # Start off by simply tagging our base image
        # All subsequents steps here will just move the tag to the newly built image
        tag_base_image(build_info)

        # One can opt out by setting image.aladdinize: false
        if build_info.aladdinize:
            aladdinize_image(build_info)

        # One can opt out by not providing a Dockerfile in the component directory
        if build_info.specialized_dockerfile:
            build_specialized_image(build_info)

        # Extract some values from the base image for the build info
        python_version, user_info = get_base_image_info(build_info)
        # Set the python version so the builder image can use the same
        # python version as the base image
        build_info.set_language_version(python_version)
        # Set the user info from the image so we can install poetry
        # and python libraries in the correct location
        build_info.set_user_info(user_info)

        # Opt out by setting image.add_poetry: false
        if build_info.add_poetry:
            add_poetry(build_info)

        # Add the component dependencies' assets
        add_dependencies(build_info)

        # Add the component's assets
        add_component(build_info, build_info.component)

    except Exception:
        logger.error("Failed to build image for component: %s", build_info.component)
        raise
    else:
        logger.success("Built image for component: %s\n\n", build_info.component)


def tag_base_image(build_info: BuildInfo):
    """
    Tag the starting point image.

    Most components will build of the default image (hopefully always somewhat close to the latest
    python release).

    If one does not wish to use the default image, provide another in the image.base field of the
    component.yaml.
    """
    logger.info(
        "Tagging base image '%s' for %s component", build_info.base_image, build_info.component
    )
    _check_call(["docker", "tag", build_info.base_image, build_info.tag])


def aladdinize_image(build_info: BuildInfo):
    """
    Add the aladdin boilerplate.

    This creates the aladdin-user user and sets the WORKDIR to /code.

    If one does not wish to add the aladdin boilerplate, specify image.aladdinize as false in the
    component.yaml.
    """
    logger.info("Adding aladdin boilerplate to %s component", build_info.component)
    _docker_build(
        dockerfile="build/python/aladdinize.dockerfile",
        tag=build_info.tag,
        buildargs=dict(FROM_IMAGE=build_info.tag, PYTHON_OPTIMIZE=build_info.python_optimize),
    )


@dockerignore("w")
def add_poetry(build_info: BuildInfo, ignore_file: DockerIgnore):
    """
    Add the poetry package manager to the image.

    This allows one to use the image to create/modify the pyproject.toml and poetry.lock files
    for a component.
    """
    logger.info("Adding poetry to %s component", build_info.component)
    ignore_file.ignore_all()
    ignore_file.include("pip.conf")
    ignore_file.include("poetry.toml")
    ignore_file.ignore_defaults()

    _docker_build(
        dockerfile="build/python/add-poetry.dockerfile",
        tag=build_info.tag,
        buildargs=dict(
            BUILDER_IMAGE=build_info.builder_image,
            FROM_IMAGE=build_info.tag,
            POETRY_VERSION=build_info.poetry_version,
            USER_HOME=build_info.user_info.home,
            USER_CHOWN=build_info.user_info.chown,
        ),
    )


def build_specialized_image(build_info: BuildInfo):
    """
    Apply the component's Dockerfile to the image.

    This allows one to further customize the (possibly aladdinized) base image with more specific
    Dockerfile instructions. The context provided to the Dockerfile is the full components/
    directory, minus the .dockerignore items, of course.
    """
    logger.info(
        "Building specialized image for %s component (dockerfile=%s)",
        build_info.component,
        build_info.specialized_dockerfile,
    )

    _docker_build(
        dockerfile=build_info.specialized_dockerfile,
        tag=build_info.tag,
        buildargs=dict(FROM_IMAGE=build_info.tag, PYTHON_OPTIMIZE=build_info.python_optimize),
    )


def get_base_image_info(build_info: BuildInfo) -> UserInfo:
    """Extract the user, group and home directory of the image's USER."""
    _docker_build(
        dockerfile="build/python/lobotomize.dockerfile",
        tag="user_extractor",
        buildargs=dict(FROM_IMAGE=build_info.tag),
    )

    def _call(command: str):
        return (
            subprocess.check_output(
                ["docker", "run", "--rm", "user_extractor", "/bin/sh", "-c", command]
            )
            .decode("utf8")
            .strip()
        )

    # TODO: Figure out when we can skip this discovery
    #       A component that provides these values in their component.yaml shouldn't check. (done)
    #       A component based on our default base image shouldn't check either.
    python_version = build_info.config.language_version
    user_info = build_info.config.user_info
    try:
        if python_version:
            logger.notice("Using configured python version: %s", python_version)
        else:
            try:
                python_version = _call(
                    "python -c 'import platform; print(platform.python_version())'"
                )
                assert (
                    python_version.count(".") == 2
                ), f"Unexpected python version string: {retrieved_version}"
                logger.notice("Extracted python version from base image: %s", python_version)
            except Exception:
                logger.warning("Failed to extract python version from base image")
                python_version = "3.8"

        if user_info:
            logger.notice("Using configured user info: %s", user_info)
        else:
            try:
                user_name, user_groups, user_home = _call("whoami; groups; echo $HOME").split("\n")
                user_groups = user_groups.split()
                user_info = UserInfo(
                    name=user_name, group=user_groups[0] if user_groups else None, home=user_home
                )
                logger.notice("Extracted user info from base image: %s", user_info)
            except Exception:
                logger.warning("Failed to extract user info from base image")
                user_info = UserInfo(name=None, group=None, home=None)
    finally:
        _check_call(["docker", "rmi", "user_extractor"])

    return python_version, user_info


def add_dependencies(build_info: BuildInfo):
    """
    Add all of the components' dependencies to the image.

    This will iterate over all of the dependencies found in the component's component.yaml and copy
    in the dependencies' poetry-managed libraries as well as the dependencies' code itself.
    """
    for component in build_info.dependencies:
        add_component(build_info, component)


def add_component(build_info: BuildInfo, component: str):
    """Add a component's poetry-managed libraries and the component's own code to the image."""

    logger.info("Adding %s dependency to %s component", component, build_info.component)
    if build_info.has_python_dependencies:
        add_component_python_dependencies(build_info, component)
    add_component_content(build_info, component)


@dockerignore("w")
def add_component_python_dependencies(
    build_info: BuildInfo, component: str, ignore_file: DockerIgnore
):
    # Only keep the files for performing a poetry install
    ignore_file.ignore_all()
    ignore_file.include("pip.conf")
    ignore_file.include("poetry.toml")
    ignore_file.include(f"{component}/pyproject.toml")
    ignore_file.include(f"{component}/poetry.lock")

    # Build the poetry dependencies
    _docker_build(
        dockerfile="build/python/add-component-python-dependencies.dockerfile",
        tag=build_info.tag,
        buildargs=dict(
            BUILDER_IMAGE=build_info.builder_image,
            FROM_IMAGE=build_info.tag,
            COMPONENT=component,
            POETRY_VERSION=build_info.poetry_version,
            POETRY_NO_DEV=build_info.poetry_no_dev,
            PYTHON_OPTIMIZE=build_info.python_optimize,
            USER_HOME=build_info.user_info.home,
            USER_CHOWN=build_info.user_info.chown,
        ),
    )


@dockerignore("w")
def add_component_content(build_info: BuildInfo, component: str, ignore_file: DockerIgnore):
    # Only keep the component content files
    ignore_file.ignore_all()
    ignore_file.include(component)
    ignore_file.ignore_defaults()

    # Copy the built poetry dependencies and the component code into the target image
    _docker_build(
        dockerfile="build/python/add-component-content.dockerfile",
        tag=build_info.tag,
        buildargs=dict(FROM_IMAGE=build_info.tag, PYTHON_OPTIMIZE=build_info.python_optimize),
    )


def _docker_build(dockerfile: str, tag: str, buildargs: dict = None):
    """
    A convenience wrapper for calling out to "docker build".

    We always send the same context: the components/ directory.
    """
    buildargs = buildargs or {}

    cmd = ["docker", "build"]
    for key, value in buildargs.items():
        cmd.extend(["--build-arg", f"{key}={value}"])
    cmd.extend(["--tag", tag, "-f", dockerfile, "components"])

    # Log the build command in a more readable format
    #
    # Example output:
    # DEBUG    docker build --tag fast-api-prototype-style:local -f <dockerfile> components
    #              BUILDER_IMAGE=python:3.8-slim
    #              COMPONENT=style
    #              FROM_IMAGE=fast-api-prototype-style:local
    #              POETRY_NO_DEV=
    #              POETRY_VERSION=1.0.5
    #              PYTHON_OPTIMIZE=
    #              USER_CHOWN=aladdin-user:aladdin-user
    #              USER_HOME=/home/aladdin-user
    logger.debug(
        f"docker build --tag {tag} -f {dockerfile} components"
        + "\n"
        + textwrap.indent(
            "\n".join(f"{key}={value}" for key, value in sorted(buildargs.items())), " " * 13
        )
        + "\n"
    )

    # Log the .dockerignore file contents used for the build
    with open(pathlib.Path("components") / ".dockerignore") as ignore_file:
        logger.debug(
            ".dockerignore file:\n         ================================\n%s",
            textwrap.indent(ignore_file.read(), " " * 9),
        )

    logger.debug("Docker build output:")
    _check_call(cmd)


def _check_call(cmd: typing.List):
    """Make a subprocess call and indent its output to match our python logging format."""
    ps = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    subprocess.check_call(["sed", "-e", "s/^/         /"], stdin=ps.stdout)
    ps.wait()


if __name__ == "__main__":
    # Install some nice logging tools
    logging.setLoggerClass(verboselogs.VerboseLogger)
    coloredlogs.install(
        level=logging.DEBUG,
        fmt="%(levelname)-8s %(message)s",
        level_styles=dict(
            spam=dict(color="green", faint=True),
            debug=dict(color="black", bold=True),
            verbose=dict(color="blue"),
            info=dict(color="cyan"),
            notice=dict(color="magenta"),
            warning=dict(color="yellow"),
            success=dict(color="green", bold=True),
            error=dict(color="red"),
            critical=dict(color="red", bold=True),
        ),
    )

    # This will be a VerboseLogger
    logger = logging.getLogger(__name__)

    # Discover the project name for reporting/tagging purposes
    with open("lamp.json") as file:
        lamp = json.load(file)

    # Let's get to it!
    build(lamp=lamp, hash=os.getenv("HASH", "local"), components=sys.argv[1:])
