import json
import logging.config
import os
import shutil
import subprocess
import venv
from os import mkdir, path
from socket import AF_INET, SOCK_STREAM, socket
from time import time
from typing import List
from uuid import uuid4
from zipfile import ZipFile

from server.errors import ApplicationInitError
from server.settings import settings
from server.validation import ENV_FILE_NAME, REQUIREMENTS_FILE_NAME
from tornado.httpclient import AsyncHTTPClient


class UnitService:
    BASE_URL = f'http://{settings.UNIT_HOST}:{settings.UNIT_PORT}/config'
    MODIFIED_AT_ENV = 'APPGEN'

    client = AsyncHTTPClient()

    async def register_app(self, app_uid: str, environment_data: dict) -> int:
        """Регистрирует приложение в файловой системе

        :param app_uid: uid приложения
        :param environment_data: переменные среды приложения
        :returns порт, по которому доступно приложение
        """

        environment = {f'{self.MODIFIED_AT_ENV}': str(time()), **environment_data}

        unit_app_path = os.path.join(settings.MOUNTED_APPS_PATH, app_uid)
        venv_dir = os.path.join(unit_app_path, 'venv')

        app_data = {
            'type': 'python 3',
            'path': unit_app_path,
            'module': 'application',
            'home': venv_dir,
            'environment': environment,
        }
        app_url = f'{self.BASE_URL}/applications/{app_uid}/'

        await self.client.fetch(app_url, body=json.dumps(app_data), method='PUT')

        log_event('registered app configuration', app_uid)

        app_port = get_unused_port()

        listener_url = f'{self.BASE_URL}/listeners/*:{app_port}/'
        listener_data = {'pass': f'applications/{app_uid}'}

        await self.client.fetch(
            listener_url, body=json.dumps(listener_data), method='PUT'
        )

        log_event('listener registered on port %s', app_uid, app_port)

        return app_port

    async def unregister_app(self, app_uid: str, app_port: int) -> None:
        """Удаляет приложение из конфигурации

        :param app_uid: uid приложения
        :param app_port: порт приложения
        """

        listener_url = f'{self.BASE_URL}/listeners/*:{app_port}/'
        await self.client.fetch(listener_url, method='DELETE')

        log_event('unregistered listener on port %s', app_uid, app_port)

        app_url = f'{self.BASE_URL}/applications/{app_uid}/'
        await self.client.fetch(app_url, method='DELETE')

        log_event('unregistered completely', app_uid)

    async def reload_app(self, app_uid: str) -> None:
        """Перезагружает приложение через обновление переменной среды.
        Сейчас документация предлагает только такой способ

        :param app_uid: uid приложения
        """

        updated_modification_time = time()

        app_env_url = (
            f'{self.BASE_URL}/applications/{app_uid}/environment/{self.MODIFIED_AT_ENV}'
        )

        res = await self.client.fetch(
            app_env_url,
            body=str(updated_modification_time),
            method='PUT',
            raise_error=False,
        )
        if res.code == 400:
            print(res.body.decode())
            raise Exception('shit')

        log_event('app configuration updated', app_uid)

    async def reset_configuration(self) -> None:
        """Сбрасывает всю конфигурацию - удаляет приложения и порты"""

        config = {'applications': {}, 'listeners': {}}
        request_data = json.dumps(config)
        await self.client.fetch(self.BASE_URL, body=request_data, method='PUT')


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
            exception = rule['exception']
            raise exception()


def parse_environment_variables(env_file_path: str) -> dict:
    """
    Считывает переменные среды приложения и записывает в локальную структуру.

    :param env_file_path: путь до файла с переменными окружения.
    :return: распарсенные переменные среды.
    """

    with open(env_file_path, 'r') as file:
        variables = [variable_line.split('=') for variable_line in file]
        return {name: value for name, value in variables}


def get_app_environment_data(app_uid: str) -> dict:
    app_path = os.path.join(settings.apps_path, app_uid)
    env_path = os.path.join(app_path, ENV_FILE_NAME)
    return parse_environment_variables(env_path)


def load_app_requirements(app_dir: str) -> None:
    """
    Создаёт окружение в директории приложения и
    устанавливает зависимости.

    :param app_dir: путь до приложения.
    """

    venv_dir = path.join(app_dir, 'venv')
    venv.create(venv_dir, with_pip=True)

    subprocess.check_call(
        ['venv/bin/pip', 'install', '-r', REQUIREMENTS_FILE_NAME], cwd=app_dir
    )


def clear_app_directory(app_dirpath: str) -> None:
    for filename in os.listdir(app_dirpath):
        file_path = os.path.join(app_dirpath, filename)

        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


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
        app_dirpath = path.join(settings.apps_path, application_uid)

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

    log_event('virtual environment created', app_uid)

    return app_uid


def get_unused_port() -> int:
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.bind((settings.UNIT_HOST, 0))
        return sock.getsockname()[1]


def destroy_application_environment(app_uid: str) -> None:
    """
    Удаляет окружение приложения из фс.

    :param app_uid: uid приложения.
    """

    app_dirpath = path.join(settings.apps_path, app_uid)
    shutil.rmtree(app_dirpath)

    log_event('virtual environment destroyed', app_uid)


async def update_application_environment(app_uid: str, package: 'ZipFile') -> None:
    """
    Полностью обновляет содержимое приложения,
    переустанавливает зависимости.

    :param app_uid: uid приложения, содержимое которого нужно обновить.
    :param package: zip архив с новыми файлами приложения и зависимостей.
    """

    app_dirpath = os.path.join(settings.apps_path, app_uid)

    clear_app_directory(app_dirpath)
    package.extractall(app_dirpath)
    load_app_requirements(app_dirpath)

    log_event('virtual environment updated', app_uid)


def log_event(message: str, app_uid: str, *args):
    extra_args = {'app_uid': app_uid}
    if args:
        logging.info(message, *args, extra=extra_args)
    else:
        logging.info(message, extra=extra_args)
