import sys
import venv
import subprocess
from uuid import uuid4
from typing import List
from zipfile import ZipFile
from os import path, mkdir, chdir, pardir

from src.consts import APP_ID_LENGTH, DEFAULT_APPS_BASE_DIR


def validate_package(package: 'ZipFile', rules: List[dict]) -> None:
    for rule in rules:
        constraint_is_fulfilled = rule['constraint']
        if not constraint_is_fulfilled(package):
            exception = rule['exception']
            raise exception


def create_application_environment(package: 'ZipFile') -> str:
    app_id = uuid4().hex[:APP_ID_LENGTH]

    app_dirpath = path.join(DEFAULT_APPS_BASE_DIR, app_id)
    mkdir(app_dirpath)

    package.extractall(app_dirpath)

    venv_dirpath = path.join(app_dirpath, 'venv')
    venv.create(venv_dirpath)

    # command = 'source venv/bin/activate'
    # process = subprocess.Popen(command.split(), cwd=app_dirpath)
    # process.communicate()

    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', '-r' 'requirements.txt'],
        cwd=app_dirpath
    )

    return app_id
