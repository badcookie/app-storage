FROM python:3.7

ENV PYTHONPATH "${PYTHONPATH}:src/"
ENV PROJECT ${PROJECT_NAME:-app_storage}
ENV POETRY_VERSION 1.0.9

RUN pip install "poetry==$POETRY_VERSION"

RUN mkdir /apps
RUN mkdir /$PROJECT

WORKDIR /$PROJECT
COPY poetry.lock pyproject.toml /$PROJECT/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . /$PROJECT

CMD ["python3", "src/server.py"]
