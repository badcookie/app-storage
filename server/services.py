import json
import os
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


def generate_app_id() -> str:
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

        application_id = generate_app_id()
        app_dirpath = path.join(settings.APPS_DIR, application_id)

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
    apps_path, app_id = path.split(app_dir)

    package.extractall(app_dir)
    load_app_requirements(app_dir)

    return app_id


def get_unused_port() -> int:
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.bind((settings.UNIT_HOST, 0))
        return sock.getsockname()[1]


async def add_unit_listener(app_id: str) -> int:
    """
    Делает запрос n/unit на добавление адреса, по
    которому будет доступно приложение.

    :param app_id: id приложения.
    :return: порт, который приложение будет слушать.
    """

    app_port = get_unused_port()
    url = f'{BASE_URL}/listeners/{settings.UNIT_HOST}:{app_port}/'
    listener_data = {'pass': f'applications/{app_id}'}
    request_body = json.dumps(listener_data)
    response = await client.fetch(
        url, body=request_body, method='PUT', raise_error=False
    )
    print(response.body.decode())
    return app_port


async def add_unit_application(app_id: str) -> None:
    """
    Делает запрос n/unit на добавление приложения в конфигурацию.

    :param app_id: id приложения.
    """

    apps_dir = '/apps/'
    app_dir = os.path.join(apps_dir, app_id)
    venv_dir = os.path.join(app_dir, 'venv')

    app_data = {
        'type': 'python 3',
        'path': app_dir,
        'module': 'application',
        'home': venv_dir,
    }
    request_body = json.dumps(app_data)
    url = f'{BASE_URL}/applications/{app_id}/'
    response = await client.fetch(
        url, body=request_body, method='PUT', raise_error=False
    )
    print(response.body.decode())


async def register_app(app_id: str) -> int:
    """
    Точка входа для регистрации приложения в n/unit.
    Делает запрос на обновление конфигурации.

    :param app_id: id приложения.
    :return: порт, который приложение будет слушать.
    """

    await add_unit_application(app_id)
    app_port = await add_unit_listener(app_id)
    return app_port
