import venv
import subprocess
from uuid import uuid4
from typing import List
from os import path, mkdir
from zipfile import ZipFile

from src.consts import (
    APPS_DIR,
    APP_ID_LENGTH,
    APP_ID_CREATION_TRIES_COUNT,
)
from src.errors import ApplicationInitError


def validate_package(package: 'ZipFile', rules: List[dict]) -> None:
    for rule in rules:
        constraint_is_fulfilled = rule['constraint']
        if not constraint_is_fulfilled(package):
            raise rule['exception']


def load_app_requirements(app_dir: str) -> None:
    venv_dir = path.join(app_dir, 'venv')
    venv.create(venv_dir, with_pip=True)

    subprocess.check_call(
        ['venv/bin/pip', 'install', '-r' 'requirements.txt'],
        cwd=app_dir
    )


def create_application_environment(package: 'ZipFile') -> str:

    def init_app_dir(try_count: int) -> str:            # TODO: test this stuff
        if try_count == APP_ID_CREATION_TRIES_COUNT:
            raise ApplicationInitError

        application_id = uuid4().hex[:APP_ID_LENGTH]
        app_dirpath = path.join(APPS_DIR, application_id)

        if not path.exists(app_dirpath):
            mkdir(app_dirpath)
            return app_dirpath

        init_app_dir(try_count + 1)

    app_dir = init_app_dir(0)
    app_path, app_id = path.split(app_dir)

    package.extractall(app_dir)

    load_app_requirements(app_dir)

    return app_id
