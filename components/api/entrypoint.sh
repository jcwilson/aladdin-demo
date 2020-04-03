#!/bin/sh
set -eu

if $APM_ENABLED; then
    echo "APM tracing enabled: $DATADOG_SERVICE_NAME"
    # start our server through ddtrace-run, which will allow us to see apm tracing in datadog
    cd api
    exec ddtrace-run uvicorn \
        --no-access-log \
        --no-use-colors \
        --uds /run/socks/uvicorn.sock \
        --workers "$UVICORN_WORKERS" \
        run:app
else
    echo "APM tracing disabled"
    cd api
    exec uvicorn \
        --no-access-log \
        --no-use-colors \
        --uds /run/socks/uvicorn.sock \
        --workers "$UVICORN_WORKERS" \
        --log-level debug \
        ${UVICORN_AUTORELOAD:+--reload} \
        run:app
fi

