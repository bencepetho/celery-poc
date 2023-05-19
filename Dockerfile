FROM python:3.11-slim-buster AS poetry

LABEL authors="Bence Petho"

RUN apt-get update && apt-get upgrade && \
    apt-get install -y curl

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

FROM poetry AS dependencies

COPY ./poetry.lock ./pyproject.toml /app/

RUN poetry config virtualenvs.create false && \
    poetry install `test "$ENVIRONMENT" == production && echo "--no-dev"` \
                   --no-root --no-cache --no-interaction --directory=/app

FROM dependencies AS app

COPY ./.env.example /app/.env
COPY ./app /app/

ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
