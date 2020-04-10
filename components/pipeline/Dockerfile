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
COPY commands/requirements.txt commands-requirements.txt
COPY pipeline/requirements.txt pipeline-requirements.txt

# Install requirements into ~/.local where they'll be easy to copy out
COPY pip.conf /etc/pip.conf
RUN pip install --upgrade pip \
    && pip install --user \
        -r shared-requirements.txt \
        -r api-requirements.txt \
        -r commands-requirements.txt \
        -r pipeline-requirements.txt
    # && pip check
### END BUILD IMAGE ###


### CONTAINER IMAGE ###
FROM python:3.8-slim

# Create unprivileged user account
RUN useradd -m -U -d /home/aladdin-user aladdin-user

# Copy installed python packages from build image and include them in $PATH
COPY pip.conf /etc/pip.conf
COPY --from=builder --chown=aladdin-user:aladdin-user /root/.local /home/aladdin-user/.local
ENV PATH /home/aladdin-user/.local/bin:$PATH

# Display how old the python libraries are
RUN pip list --outdated

# Specify the directory that CMD executes from
WORKDIR /code

# Pre-compile optimized bytecode for our library code
RUN python -O -m compileall \
    && python -O -m compileall /home/aladdin-user/.local .

# Switch to the unpriveleged user account
USER aladdin-user
### END CONTAINER IMAGE ###
