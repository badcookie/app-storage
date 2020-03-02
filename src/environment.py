import subprocess
import venv
from os import mkdir, path
from typing import List
from uuid import uuid4
from zipfile import ZipFile

from src.consts import APP_ID_CREATION_TRIES_COUNT, APP_ID_LENGTH, APPS_DIR
from src.errors import ApplicationInitError


def validate_package(package: "ZipFile", rules: List[dict]) -> None:
    """
    Проверяет zip архив на соответствие условиям. Если хотя бы
    одно не выполняется, выбрасывает соответствующее исключение.

    :param package: zip файл.
    :param rules: список правил, по которым валидируется архив.
    Каждое правило состоит из функции-предиката (условия выполнения) и исключения,
    которое вызывается при невыполнении условия.
    """

    for rule in rules:
        constraint_is_fulfilled = rule["constraint"]
        if not constraint_is_fulfilled(package):
            raise rule["exception"]


def load_app_requirements(app_dir: str) -> None:
    """
    Создаёт окружение в директории приложения и
    устанавливает зависимости.

    :param app_dir: путь до приложения.
    """

    venv_dir = path.join(app_dir, "venv")
    print("Venv dir:", venv_dir)
    venv.create(venv_dir, with_pip=True)
    print("App dir before pip install:", app_dir)
    subprocess.check_call(
        ["venv/bin/pip", "install", "-r", "requirements.txt"], cwd=app_dir
    )


def generate_app_id() -> str:
    return uuid4().hex[:APP_ID_LENGTH]


def init_app() -> str:
    """
    Генерирует id приложения и создаёт
    для него директорию. Если приложение с таким id
    уже существует, пытается проделать всё то же самое
    количество раз, заданное в APP_ID_CREATION_TRIES_COUNT.

    Если ни одна попытка не пройдёт, вызовет
    исключение.

    :return: путь до созданной директории приложения.
    """

    def try_to_create_dir(try_count: int) -> str:
        if try_count == APP_ID_CREATION_TRIES_COUNT:
            raise ApplicationInitError

        application_id = generate_app_id()
        app_dirpath = path.join(APPS_DIR, application_id)

        if not path.exists(app_dirpath):
            mkdir(app_dirpath)
            return app_dirpath

        return try_to_create_dir(try_count + 1)

    return try_to_create_dir(try_count=0)


def create_application_environment(package: "ZipFile") -> str:
    """
    Создаёт директорию приложения со своим окружением,
    куда сохраняет файлы приложения и зависимостей,
    после чего устанавливает эти зависимости.

    :param package: zip архив с файлами приложения и зависимостей.
    :return: id приложения.
    """

    app_dir = init_app()
    print("App dir:", app_dir)
    apps_path, app_id = path.split(app_dir)
    print("Apps path:", apps_path)
    print("App id:", app_id)

    package.extractall(app_dir)
    load_app_requirements(app_dir)

    return app_id
