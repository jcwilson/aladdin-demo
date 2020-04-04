#!/bin/bash -eu

# Build up this command to eventually exec
UVICORN_CMD=()

if "$APM_ENABLED"; then
    # Start our server through ddtrace-run to activate Datadog APM tracing
    echo "APM tracing enabled: $DATADOG_SERVICE_NAME"
    UVICORN_CMD+=( ddtrace-run )
fi

# uvicorn invocation and general options
UVICORN_CMD+=( uvicorn --no-access-log --no-use-colors --workers "$UVICORN_WORKERS" )

if "$UVICORN_AUTORELOAD"; then
    # Listen on TCP since reloading doesn't work with Unix domain sockets
    UVICORN_CMD+=( --port "$UVICORN_PORT" --reload --reload-dir . )
else
    UVICORN_CMD+=( --uds "/run/socks/${UVICORN_DOMAIN_SOCKET}" )
fi

# Specify the module and app name for the uvicorn app
UVICORN_CMD+=( api.run:app )

# Invoke the command
exec "${UVICORN_CMD[@]}"
