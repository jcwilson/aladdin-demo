### BUILD POETRY PACKAGE MANAGER #######################################################
# This downloads, installs and configures the poetry tool under the root user in the
# build image.
########################################################################################
ARG BUILDER_IMAGE
ARG FROM_IMAGE

FROM $BUILDER_IMAGE as builder

# Configure pip
COPY pip.conf /etc/pip.conf

# Install poetry under the aladdin-user, then switch back to root
ARG POETRY_VERSION=1.0.5
ADD https://raw.githubusercontent.com/python-poetry/poetry/${POETRY_VERSION}/get-poetry.py /tmp/get-poetry.py
RUN python /tmp/get-poetry.py

# Configure poetry
COPY poetry.toml /root/.config/pypoetry/config.toml
########################################################################################



### BUILD POETRY PACKAGE MANAGER #######################################################
# Copy the poetry tool and its configuration into the target image. This also includes
# a bit of pip global configuration since poetry uses it under the hood (as do our
# own tools).
########################################################################################
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
