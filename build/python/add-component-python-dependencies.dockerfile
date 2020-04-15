### MULTISTAGE BUILD ###################################################################
# Set up the build environment. We need to build in a container that has everything
# needed to build and install our poetry dependencies that have native parts, but we'd
# rather not include gcc et al. in the final service image since they're not needed
# to run the service.
########################################################################################
ARG BUILDER_IMAGE
ARG FROM_IMAGE

FROM $BUILDER_IMAGE AS builder

# Install packages required to build native library components
RUN apt-get update \
    && apt-get -y --no-install-recommends install \
        gettext \
        gcc \
        g++ \
        make \
        libc6-dev \
    && apt-get clean

# Upgrade and configure pip
RUN pip install --upgrade pip

# Configure pip
COPY pip.conf /etc/pip.conf

# Install poetry under the root user's home directory
ARG POETRY_VERSION
ADD https://raw.githubusercontent.com/python-poetry/poetry/${POETRY_VERSION}/get-poetry.py /tmp/get-poetry.py
RUN python /tmp/get-poetry.py

# Configure poetry
COPY poetry.toml /root/.config/pypoetry/config.toml

# Move to build directory before copying items to non-fixed location
WORKDIR /build

# Copy the component's poetry files
# This assumes the build script has omitted everything but the component's poetry
# files, like {component}/pyproject.toml and {component}/poetry.lock from the context
# with a just-in-time created .dockerignore file.
COPY . .

# Install our project dependencies if they are specified in the pyproject.toml and
# poetry.lock files. Otherwise, this is a no-op.
ARG COMPONENT
ARG POETRY_NO_DEV
ARG PYTHON_OPTIMIZE
RUN cd "$COMPONENT" \
    && . /root/.poetry/env \
    && poetry install $POETRY_NO_DEV \
    && python $PYTHON_OPTIMIZE -m compileall /root/.local
### END MULTISTAGE BUILD ###############################################################
# We can now copy the contents of /root/.local to our concrete image
########################################################################################




### POPULATE IMAGE BUILD ###############################################################
# This is where we copy the results of the python library installation into our eventual
# concrete image, leaving all the build tooling behind.
########################################################################################
FROM $FROM_IMAGE
ARG USER_HOME
ARG USER_CHOWN

# Copy installed python packages from build image and include them in $PATH
COPY --from="builder" --chown=$USER_CHOWN /root/.local $USER_HOME/.local

# Check that our libraries still don't have conflicts
RUN pip check
### END POPULATE IMAGE BUILD ###########################################################
# We now have the beginnings of a functional image with the python dependencies specific
# to the component we're building it for. This process will be repeated for all of a
# component's dependency components and then one final time for the component itself.
########################################################################################
