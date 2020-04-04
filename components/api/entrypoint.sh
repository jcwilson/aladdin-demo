#!/bin/sh
set -eu

if $APM_ENABLED; then
    echo "APM tracing enabled: $DATADOG_SERVICE_NAME"
    # start our server through ddtrace-run, which will allow us to see apm tracing in datadog
    exec ddtrace-run uvicorn \
        --no-access-log \
        --no-use-colors \
        --uds /run/socks/uvicorn.sock \
        --workers "$UVICORN_WORKERS" \
        api.run:app
else
    echo "APM tracing disabled"
    exec uvicorn \
        --no-access-log \
        --no-use-colors \
        --uds /run/socks/uvicorn.sock \
        --workers "$UVICORN_WORKERS" \
        --log-level debug \
        ${UVICORN_AUTORELOAD:+--reload} \
        api.run:app
fi

