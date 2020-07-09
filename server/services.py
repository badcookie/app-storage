import json
import os
import shutil
import subprocess
import venv
from os import mkdir, path
from socket import AF_INET, SOCK_STREAM, socket
from typing import List
from uuid import uuid4
from zipfile import ZipFile

from server.exceptions import ApplicationInitError
from server.settings import settings
from tornado.httpclient import AsyncHTTPClient

BASE_URL = f'http://{settings.UNIT_HOST}:{settings.UNIT_PORT}/config'

client = AsyncHTTPClient()


def validate_package(package: 'ZipFile', rules: List[dict]) -> None:
    """
    Проверяет zip архив на соответствие условиям. Если хотя бы
    одно не выполняется, выбрасывает соответствующее исключение.

    :param package: zip файл.
    :param rules: список правил, по которым валидируется архив.
    Каждое правило состоит из функции-предиката (условия выполнения) и исключения,
    которое вызывается при невыполнении условия.
    """

    for rule in rules:
        constraint_is_fulfilled = rule['constraint']
        if not constraint_is_fulfilled(package):
            raise rule['exception']


def load_app_requirements(app_dir: str) -> None:
    """
    Создаёт окружение в директории приложения и
    устанавливает зависимости.

    :param app_dir: путь до приложения.
    """

    venv_dir = path.join(app_dir, 'venv')
    venv.create(venv_dir, with_pip=True)

    subprocess.check_call(
        ['venv/bin/pip', 'install', '-r', 'requirements.txt'], cwd=app_dir
    )


def generate_app_uid() -> str:
    return uuid4().hex[: settings.APP_ID_LENGTH]


def create_app_directory() -> str:
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
        if try_count == settings.APP_ID_CREATION_TRIES_COUNT:
            raise ApplicationInitError

        application_uid = generate_app_uid()
        app_dirpath = path.join(settings.APPS_DIR, application_uid)

        if not path.exists(app_dirpath):
            mkdir(app_dirpath)
            return app_dirpath

        return try_to_create_dir(try_count + 1)

    return try_to_create_dir(try_count=0)


def create_application_environment(package: 'ZipFile') -> str:
    """
    Точка входа для создания приложения в файловой системе.
    Создаёт директорию приложения со своим окружением,
    куда сохраняет файлы приложения и зависимостей,
    после чего устанавливает эти зависимости.

    :param package: zip архив с файлами приложения и зависимостей.
    :return: id приложения.
    """

    app_dir = create_app_directory()
    apps_path, app_uid = path.split(app_dir)

    package.extractall(app_dir)
    load_app_requirements(app_dir)

    return app_uid


def get_unused_port() -> int:
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.bind((settings.UNIT_HOST, 0))
        return sock.getsockname()[1]


async def register_app(app_uid: str) -> int:
    """
    Регистрирует приложение в n/unit, делая
    запросы на обновление конфигурации.

    :param app_uid: uid приложения.
    :return: порт, который приложение будет слушать.
    """

    apps_dir = '/apps/'
    app_dir = os.path.join(apps_dir, app_uid)
    venv_dir = os.path.join(app_dir, 'venv')

    app_data = {
        'type': 'python 3',
        'path': app_dir,
        'module': 'application',
        'home': venv_dir,
    }
    request_body = json.dumps(app_data)
    app_url = f'{BASE_URL}/applications/{app_uid}/'
    await client.fetch(app_url, body=request_body, method='PUT')

    app_port = get_unused_port()
    listener_url = f'{BASE_URL}/listeners/{settings.UNIT_HOST}:{app_port}/'
    listener_data = {'pass': f'applications/{app_uid}'}
    request_body = json.dumps(listener_data)
    await client.fetch(listener_url, body=request_body, method='PUT')

    return app_port


def destroy_application_environment(app_uid: str) -> None:
    """
    Удаляет окружение приложения из фс.

    :param app_uid: uid приложения.
    """

    app_dirpath = path.join(settings.APPS_DIR, app_uid)
    shutil.rmtree(app_dirpath)


async def unregister_app(app_uid: str, app_port: int) -> None:
    """
    Удаляет данные о приложении из конфигурации n/unit.

    :param app_uid: uid приложения.
    :param app_port: порт, который приложение слушает.
    """

    listener_url = f'{BASE_URL}/listeners/{settings.UNIT_HOST}:{app_port}/'
    await client.fetch(listener_url, method='DELETE')

    app_url = f'{BASE_URL}/applications/{app_uid}/'
    await client.fetch(app_url, method='DELETE')
