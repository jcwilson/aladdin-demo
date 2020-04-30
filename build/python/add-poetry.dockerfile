### INSTALL POETRY PACKAGE MANAGER #######################################################
# Copy the poetry tool and its configuration into the target image. This also includes
# a bit of pip global configuration since poetry uses it under the hood (as do our
# own tools).
########################################################################################
ARG BUILDER_IMAGE
ARG FROM_IMAGE

# We'll copy over the builder image's poetry installation
FROM $BUILDER_IMAGE as builder

FROM $FROM_IMAGE

ARG USER_CHOWN=root:root
ARG USER_HOME=/root

# Configure pip
COPY --from="builder" /etc/pip.conf /etc/pip.conf

# Copy installed python packages from build image and include them in $PATH
COPY --from="builder" --chown=$USER_CHOWN /root/.poetry $USER_HOME/.poetry

# Configure poetry
COPY --from="builder" /root/.config/pypoetry $USER_HOME/.config/pypoetry

# Add poetry directories to PATH
ENV PATH $USER_HOME/.local/bin:$USER_HOME/.poetry/bin:$PATH
