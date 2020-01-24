import venv
import subprocess
from uuid import uuid4
from typing import List
from zipfile import ZipFile
from os import path, mkdir, environ

from src.consts import (
    APP_ID_LENGTH,
    BASE_VENV_DIR,
    DEFAULT_APPS_BASE_DIR,
)


def activate_venv(venv_dir: str) -> None:
    environ['VIRTUAL_ENV'] = venv_dir


def validate_package(package: 'ZipFile', rules: List[dict]) -> None:
    for rule in rules:
        constraint_is_fulfilled = rule['constraint']
        if not constraint_is_fulfilled(package):
            exception = rule['exception']
            raise exception


def load_app_requirements(app_dir: str) -> None:
    venv_dir = path.join(app_dir, 'venv')
    venv.create(venv_dir, with_pip=True)

    activate_venv(venv_dir)
    subprocess.check_call(
        ['venv/bin/pip', 'install', '-r' 'requirements.txt'],
        cwd=app_dir
    )
    activate_venv(BASE_VENV_DIR)


# TODO: обработка ошибок
def create_application_environment(package: 'ZipFile') -> str:
    app_id = uuid4().hex[:APP_ID_LENGTH]

    app_dir = path.join(DEFAULT_APPS_BASE_DIR, app_id)
    mkdir(app_dir)

    package.extractall(app_dir)

    load_app_requirements(app_dir)

    return app_id
