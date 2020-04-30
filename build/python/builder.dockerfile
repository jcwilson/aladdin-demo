ARG FROM_IMAGE
FROM $FROM_IMAGE

# Install packages required to build native library components
RUN apt-get update \
 && apt-get -y --no-install-recommends install \
    gettext \
    gcc \
    g++ \
    make \
    libc6-dev

# Upgrade pip
RUN pip install --upgrade pip

# Configure pip
COPY pip.conf /etc/pip.conf

# Install poetry under the root user's home directory
ARG POETRY_VERSION
ADD https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py /tmp/get-poetry.py
RUN python /tmp/get-poetry.py --version $POETRY_VERSION

# Configure poetry
COPY poetry.toml /root/.config/pypoetry/config.toml

# Move to build directory before copying items to non-fixed location
WORKDIR /build
