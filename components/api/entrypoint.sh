#!/bin/sh
set -eu

if $APM_ENABLED; then
    echo "APM tracing enabled: $DATADOG_SERVICE_NAME"
    # Start our server through ddtrace-run to activate Datadog APM tracing
    exec ddtrace-run uvicorn \
        --no-access-log \
        --no-use-colors \
        --uds /run/socks/uvicorn-api.sock \
        --workers "$UVICORN_WORKERS" \
        api.run:app
else
    echo "APM tracing disabled"
    exec uvicorn \
        --no-access-log \
        --no-use-colors \
        --uds /run/socks/uvicorn-api.sock \
        --workers "$UVICORN_WORKERS" \
        --log-level debug \
        ${UVICORN_AUTORELOAD:+--reload} \
        api.run:app
fi
