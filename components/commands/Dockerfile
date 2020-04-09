FROM fivestarsos/commands-base:2.0.0

COPY shared/requirements.txt shared-requirements.txt
COPY commands/requirements.txt commands-requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        -r shared-requirements.txt \
        -r commands-requirements.txt \
    && pip check

RUN pip list --no-cache-dir --outdated

COPY shared shared
COPY commands/commands commands
