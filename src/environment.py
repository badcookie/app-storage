import os
import venv
import subprocess
from uuid import uuid4
from typing import List
from zipfile import ZipFile

from src.consts import APP_ID_LENGTH, APPS_DIR


def validate_package(package: 'ZipFile', rules: List[dict]) -> None:
    for rule in rules:
        constraint_is_fulfilled = rule['constraint']
        if not constraint_is_fulfilled(package):
            exception = rule['exception']
            raise exception


def load_app_requirements(app_dir: str) -> None:
    venv_dir = os.path.join(app_dir, 'venv')
    venv.create(venv_dir, with_pip=True)

    subprocess.check_call(
        ['venv/bin/pip', 'install', '-r' 'requirements.txt'],
        cwd=app_dir
    )


# TODO: обработка ошибок
def create_application_environment(package: 'ZipFile') -> str:
    app_id = uuid4().hex[:APP_ID_LENGTH]

    app_dir = os.path.join(APPS_DIR, app_id)
    os.mkdir(app_dir)

    package.extractall(app_dir)

    load_app_requirements(app_dir)

    return app_id
