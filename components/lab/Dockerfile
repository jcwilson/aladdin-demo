FROM jupyter/minimal-notebook:dc9744740e12

# Copy our requirements.txt files to the docker container
COPY shared/requirements.txt shared-requirements.txt
COPY api/requirements.txt api-requirements.txt
COPY commands/requirements.txt commands-requirements.txt
COPY lab/requirements.txt lab-requirements.txt

# Install requirements into ~/.local where they'll be easy to copy out.
COPY pip.conf /etc/pip.conf
RUN pip install --upgrade pip \
    && pip install --user \
        -r shared-requirements.txt \
        -r api-requirements.txt \
        -r commands-requirements.txt \
        -r lab-requirements.txt
    # && pip check

COPY . /code

ENV PYTHONPATH /code
ENV JUPYTER_ENABLE_LAB yes
