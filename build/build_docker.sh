#!/usr/bin/env bash
set -eu -o pipefail


function docker_build {
    # Build an image for the specified component
    # It will be tagged as ${PROJECT_NAME}-${component}${suffix}:${HASH}
    local component="$1" suffix="${2:+-${2}}" dockerfile="${3:-Dockerfile}"
    local tag="${PROJECT_NAME}-${component}${suffix}:${HASH}"
    echo >&2
    echo >&2 "Building docker image \"${tag}\" for component: ${component}"
    echo >&2 "================================================================================"
    docker >&2 build -t "$tag" -f "components/${component}/${dockerfile}" components
    echo >&2

    # Return the tag value in case we need to do further work with the image
    echo "$tag"
}


# Ensure the current working dir is the repository root
BUILD_PATH="$(cd "$(dirname "$0")" || exit 1 && pwd)"
PROJECT_ROOT="$(cd "$BUILD_PATH/.." || exit 1 && pwd)"
cd "$PROJECT_ROOT" || exit 1
PROJECT_NAME="$(jq -r .name <lamp.json)"

docker_build >/dev/null api
docker_build >/dev/null commands
docker_build >/dev/null pipeline
docker_build >/dev/null lab
