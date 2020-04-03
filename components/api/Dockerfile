### BUILD IMAGE ###
# Set up the build environment.  We need to build in a container that has everything
# needed to build and install our pip dependencies that have native parts, but we'd
# rather not include gcc et al. in the final service image since they're not needed
# to run the service.
FROM python:3.8-slim AS builder

# Install packages required to build native library components
RUN apt-get update \
    && apt-get -y --no-install-recommends install \
        gettext \
        gcc \
        g++ \
        make \
        libc6-dev \
    && apt-get clean

# Copy our requirements.txt files to the docker container
COPY shared/requirements.txt shared-requirements.txt
COPY api/requirements.txt api-requirements.txt

# Install requirements into ~/.local where they'll be easy to copy out.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --user --no-cache-dir --no-warn-script-location \
        -r shared-requirements.txt \
        -r api-requirements.txt \
    && pip check
### END BUILD IMAGE ###


### SERVICE IMAGE ###
FROM python:3.8-slim

# Create unprivileged user account
RUN useradd -m -U -d /home/aladdin-user aladdin-user

# Switch to the unpriveleged user account
USER aladdin-user

# Copy installed python packages from build image and include them in $PATH.
COPY --from=builder --chown=aladdin-user:aladdin-user /root/.local /home/aladdin-user/.local
ENV PATH /home/aladdin-user/.local/bin:$PATH

# Display how old the python libraries are
RUN pip list --no-cache-dir --outdated

# Specify the directory that CMD executes from
WORKDIR /srv

# Copy over the directory into docker container with given path
COPY shared shared
COPY api api

# Ensure python can find our shared code
ENV PYTHONPATH=/srv/shared

# Run the application with uvicorn once the container has been created
ENTRYPOINT ["/bin/sh", "api/entrypoint.sh"]
### END SERVICE IMAGE ###
