#!/bin/bash -eu

# Build up this command to eventually exec
UVICORN_CMD=()

if "$APM_ENABLED"; then
    # Start our server through ddtrace-run to activate Datadog APM tracing
    echo "APM tracing enabled: $DATADOG_SERVICE_NAME"
    UVICORN_CMD+=( ddtrace-run )
fi

# uvicorn invocation and general options
UVICORN_CMD+=( uvicorn --workers "$UVICORN_WORKERS" )

if "$UVICORN_LOG_COLORS"; then
    UVICORN_CMD+=( --use-colors )
else
    UVICORN_CMD+=( --no-use-colors )
fi

if ! "$UVICORN_ACCESS_LOG"; then
    # We don't need an access log if we're behind nginx
    UVICORN_CMD+=( --no-access-log )
fi

if [[ "$UVICORN_TRANSPORT" == "UDS" ]]; then
    # Listen on a Unix domain socket file
    # This creates the file that nginx will look for
    UVICORN_CMD+=( --uds "/run/socks/${UVICORN_DOMAIN_SOCKET}" )
else
    # Listen on our TCP port
    UVICORN_CMD+=( --host "$UVICORN_HOST" --port "$UVICORN_PORT" )

    # We assume TCP has been enabled if we're enabling reload
    if "$UVICORN_AUTORELOAD"; then
        UVICORN_CMD+=( --reload --reload-dir . )
    fi
fi

# Specify the module and app name for the uvicorn app
UVICORN_CMD+=( api.run:app )

# Invoke the command
echo "Running: ${UVICORN_CMD[*]}"
exec "${UVICORN_CMD[@]}"
