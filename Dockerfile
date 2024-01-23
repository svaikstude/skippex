# References:
# https://stackoverflow.com/a/57886655/407054
# https://pythonspeed.com/docker/

# base

FROM python:3.9.18-slim as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

WORKDIR /app

# builder

FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.2.1 \
    VIRTUAL_ENV=/app/venv/

ENV PATH=$VIRTUAL_ENV/bin:$PATH

RUN python -m pip install "poetry==$POETRY_VERSION" \
    && python -m venv $VIRTUAL_ENV
RUN python -m pip install -U pip

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi

COPY . .
RUN poetry build && pip install dist/*.whl

# final

FROM base as final

LABEL org.opencontainers.image.source=https://github.com/svaikstude/skippex

VOLUME /data

# Path XDG_DATA_HOME doesn't exist.
# Variable XDG_RUNTIME_DIR isn't set.
ENV XDG_DATA_HOME=/data \
    XDG_RUNTIME_DIR=/run
RUN mkdir -p "$XDG_DATA_HOME" "$XDG_RUNTIME_DIR"

COPY docker-entrypoint.sh .
COPY ./pyproject.toml ./pyproject.toml
COPY --from=builder /app/venv /app/venv
COPY ./tests ./tests
RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]
