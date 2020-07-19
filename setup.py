import json
from os import path

ENV_FILE_NAME = '.env'
DEVELOP_SETTINGS_NAME = '.settings.json'
COMPOSE_FILE_NAME = 'docker-compose.yml'
DOCKERFILE_NAME = 'Dockerfile'


ENV_TEMPLATE = '''ENVIRONMENT={environment}
PROJECT_NAME={project_name}
APP_PORT={app_port}
APPS_DIR={apps_dir}
UNIT_PORT={unit_port}
DB={{"HOST": "{db_host}", "PORT": "{db_port}", "USER_": "{db_user}", "PASSWORD": "{db_password}"}}
'''

COMPOSE_TEMPLATE = '''version: "3.5"

services:
  unit:
    container_name: "${{PROJECT_NAME}}_unit"
    image: nginx/unit:1.15.0-python3.7
    network_mode: host
    command:
      ["unitd", "--no-daemon", "--control", "127.0.0.1:${{UNIT_PORT:-{unit_port}}}"]
    volumes:
      - apps_data:"${{APPS_DIR}}"

  server:
    container_name: "${{PROJECT_NAME}}_server"
    build:
      context: .
      dockerfile: Dockerfile
    image: "${{PROJECT_NAME}}:server"
    ports:
      - "${{APP_PORT:-{app_port}}}:${{APP_PORT:-{app_port}}}"
    volumes:
      - apps_data:"${{APPS_DIR}}"

  db:
    image: mongo
    container_name: "${{PROJECT_NAME}}_db"
    volumes:
      - db_data:/data/db
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${{DB_USER}}
      MONGO_INITDB_ROOT_PASSWORD: ${{DB_PASSWORD}}
    ports:
      - "${{DB_PORT:-{db_port}}}:27017"

volumes:
  apps_data: {{}}
  db_data: {{}}
'''

DOCKERFILE_TEMPLATE = '''FROM python:3.7

RUN pip install poetry

RUN mkdir {apps_dir}
RUN mkdir /app_storage

WORKDIR /app_storage
COPY poetry.lock pyproject.toml /app_storage/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . /app_storage

CMD ["python3", "server/app.py"]

'''


def get_default_settings():
    return {
        'environment': 'development',
        'project_name': 'app_storage',
        'db_host': 'localhost',
        'db_port': '27017',
        'db_user': 'badcookie',
        'db_password': 'password',
        'app_port': '8000',
        'apps_dir': '/apps/',
        'unit_port': '9000',
    }


if __name__ == '__main__':
    if not path.isfile(DEVELOP_SETTINGS_NAME):
        with open(DEVELOP_SETTINGS_NAME, 'w') as f:
            json.dump(get_default_settings(), f, indent=4)

    with open(DEVELOP_SETTINGS_NAME) as f:
        settings = json.load(f)

    with open(ENV_FILE_NAME, 'w') as f:
        f.write(ENV_TEMPLATE.format(**settings))

    with open(COMPOSE_FILE_NAME, 'w') as f:
        f.write(COMPOSE_TEMPLATE.format(**settings))

    with open(DOCKERFILE_NAME, 'w') as f:
        f.write(DOCKERFILE_TEMPLATE.format(**settings))
