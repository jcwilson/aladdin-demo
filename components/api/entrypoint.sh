#!/bin/bash -eu

# Build up this command to eventually exec
uvicorn_cmd=()

if "$APM_ENABLED"; then
    # Start our server through ddtrace-run to activate Datadog APM tracing
    echo "APM tracing enabled: $DATADOG_SERVICE_NAME"
    uvicorn_cmd+=( ddtrace-run )
fi

# uvicorn invocation and general options
uvicorn_cmd+=( uvicorn --workers "$UVICORN_WORKERS" )

if "$UVICORN_LOG_COLORS"; then
    uvicorn_cmd+=( --use-colors )
else
    uvicorn_cmd+=( --no-use-colors )
fi

if ! "$UVICORN_ACCESS_LOG"; then
    # We don't need an access log if we're behind nginx
    uvicorn_cmd+=( --no-access-log )
fi

if [[ "$UVICORN_TRANSPORT" == "UDS" ]]; then
    # Listen on a Unix domain socket file
    # This creates the file that nginx will look for
    uvicorn_cmd+=( --uds "/run/socks/${UVICORN_DOMAIN_SOCKET}" )
else
    # Listen on our TCP port
    uvicorn_cmd+=( --host "$UVICORN_HOST" --port "$UVICORN_PORT" )

    # We assume TCP has been enabled if we're enabling reload
    if "$UVICORN_AUTORELOAD"; then
        uvicorn_cmd+=( --reload --reload-dir . )
    fi
fi

# Specify the module and app name for the uvicorn app
uvicorn_cmd+=( api.run:app )

# Invoke the command
echo "Running: ${uvicorn_cmd[*]}"
exec "${uvicorn_cmd[@]}"
