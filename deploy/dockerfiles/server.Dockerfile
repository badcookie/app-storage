FROM python:3.7

RUN pip install poetry

RUN mkdir /apps/
RUN mkdir /app_storage
RUN mkdir /app_storage/client/

WORKDIR /app_storage
COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY server /app_storage/server/

CMD ["python3", "server/app.py"]
