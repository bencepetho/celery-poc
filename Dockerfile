FROM python:3.11-slim-buster AS poetry_base

LABEL authors="Bence Petho"

WORKDIR /code

RUN apt-get update && apt-get upgrade && \
    apt-get install -y curl

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

FROM poetry_base AS app

COPY ./poetry.lock ./pyproject.toml ./

RUN poetry config virtualenvs.create false && \
    poetry install `test "$ENVIRONMENT" == production && echo "--no-dev"` \
                   --no-root --no-cache --no-interaction

COPY ./app ./app

ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
