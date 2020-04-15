########################################################################################
# Just dumps a provided message to stdout
########################################################################################

FROM busybox

# Place the message into the environment so /bin/sh can expand it
ARG MESSAGE
ENV MESSAGE $MESSAGE

ENTRYPOINT ["/bin/sh", "-c", "echo \"$MESSAGE\""]
