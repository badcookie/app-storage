import json
import logging.config
import os
import shutil
import subprocess
import venv
from abc import ABC, abstractmethod
from functools import partial
from os import mkdir, path
from socket import AF_INET, SOCK_STREAM, socket
from time import time
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4
from zipfile import ZipFile

from server.errors import ApplicationInitError
from server.settings import Environment, settings
from server.validation import ENV_FILE_NAME, REQUIREMENTS_FILE_NAME
from tornado.httpclient import AsyncHTTPClient

if TYPE_CHECKING:
    from docker import DockerClient


class UnitService(ABC):
    INITIAL_CONFIG_PATH = os.path.join(settings.BASE_DIR, 'unit_config.json')
    BASE_URL = f'http://{settings.UNIT_HOST}:{settings.UNIT_PORT}/config'
    MODIFIED_AT_ENV_NAME = 'MODIFIED_AT'

    client = AsyncHTTPClient()

    def __init__(self):
        self.URLS = {
            'routes': lambda: f'{self.BASE_URL}/routes/',
            'application': lambda app_uid: f'{self.BASE_URL}/applications/{app_uid}/',
            'app_route': lambda app_uid: f'{self.BASE_URL}/routes/{app_uid}/',
            'app_env': lambda app_uid: f'{self.BASE_URL}/applications/{app_uid}/environment/',  # NOQA
        }

    async def _load_application(self, app_uid: str, env_data: dict) -> None:
        """Добавляет/обновляет инстанс unit приложения в коллекции приложений

        :param app_uid: uid приложения
        :param env_data: переменные среды приложения
        """

        app_dirpath = os.path.join(settings.MOUNTED_APPS_PATH, app_uid)
        wsgi_module = env_data.get('ENTRYPOINT')

        app_creation_ts = str(time())
        environment = {
            **env_data,
            f'{self.MODIFIED_AT_ENV_NAME}': app_creation_ts,
        }

        app_data = {
            'type': 'python 3',
            'path': env_data.get('PROJECT_WORKDIR') or app_dirpath,
            'module': wsgi_module,
            'home': 'venv',
            'environment': environment,
            'working_directory': app_dirpath,
        }
        app_url = self.URLS['application'](app_uid)

        await self.client.fetch(app_url, body=json.dumps(app_data), method='PUT')

        log_event('registered app configuration', app_uid)

    async def _remove_application(self, app_uid: str) -> None:
        """Удаляет инстанс unit приложения из коллекции приложений

        :param app_uid: uid приложения
        """

        app_url = self.URLS['application'](app_uid)
        await self.client.fetch(app_url, method='DELETE', raise_error=False)

        log_event('unregistered application', app_uid)

    @abstractmethod
    def register_app(self, app_uid: str, environment_data: dict) -> Optional[dict]:
        """Регистрирует полную конфигурацию приложения в unit

        :param app_uid: uid приложения
        :param environment_data: переменные среды приложения
        :return метаданные приложения из unit
        """
        ...

    @abstractmethod
    def unregister_app(self, app_uid: str) -> None:
        """Удаляет полную конфигурацию приложения из unit

        :param app_uid: uid приложения
        """
        ...

    async def reset_configuration(self) -> None:
        """Сбрасывает всю конфигурацию unit до дефолтного состояния"""

        with open(self.INITIAL_CONFIG_PATH) as config:
            request_data = config.read().strip('\n')
            await self.client.fetch(self.BASE_URL, body=request_data, method='PUT')

    async def get_app_environment_data(self, app_uid: str) -> dict:
        """Забирает из конфигурации переменные среды приложения

        :param app_uid: uid приложения
        :return: переменные среды приложения
        """

        app_env_url = self.URLS['app_env'](app_uid)
        response = await self.client.fetch(app_env_url, method='GET')
        response_data = response.body.decode()
        return json.loads(response_data)


class ProductionUnitService(UnitService):
    async def _load_routes(self, app_uid: str, env_data: dict) -> None:
        """Добавляет условия, которые при выполнении перенаправляют
        запрос нужному приложению

        :param app_uid: uid приложения
        :param env_data: переменные среды приложения
        """

        app_dirpath = os.path.join(settings.MOUNTED_APPS_PATH, app_uid)
        static_path = env_data.get('STATIC_PATH')
        routes_url = self.URLS['routes']()

        if static_path:
            absolute_static_path = os.path.join(app_dirpath, static_path)
            static_route = {
                'match': {
                    'host': f'{app_uid}.{settings.PROJECT_ADDRESS}',
                    'uri': '/static/*',
                },
                'action': {'share': absolute_static_path},
            }

            await self.client.fetch(
                routes_url, body=json.dumps(static_route), method='POST'
            )

        app_route = {
            'match': {'host': f'{app_uid}.{settings.PROJECT_ADDRESS}'},
            'action': {'pass': f'applications/{app_uid}'},
        }

        await self.client.fetch(routes_url, body=json.dumps(app_route), method='POST')

        log_event('registered app routing', app_uid)

    async def register_app(self, app_uid: str, environment_data: dict) -> None:
        await self._load_application(app_uid, environment_data)
        await self._load_routes(app_uid, environment_data)

    @staticmethod
    def _is_deleted_app_route(deleted_app_uid: str, route: dict) -> bool:
        condition = route['match']
        expected_host = condition['host']

        app_uid, *_ = expected_host.split('.')
        return app_uid == deleted_app_uid

    async def _remove_routes(self, app_uid: str) -> None:
        """Удаляет матчеры заданного приложения, которые
        перенаправляют ему запросы

        :param app_uid: uid приложения
        """

        routes_url = self.URLS['routes']()

        routes_response = await self.client.fetch(routes_url, method='GET')
        response_data = routes_response.body.decode()

        routes = json.loads(response_data)

        is_deleted_app_route = partial(self._is_deleted_app_route, app_uid)
        filtered_routes = [route for route in routes if not is_deleted_app_route(route)]

        await self.client.fetch(
            routes_url,
            body=json.dumps(filtered_routes),
            method='PUT',
            raise_error=False,
        )

        log_event('unregistered routes', app_uid)

    async def unregister_app(self, app_uid: str) -> None:
        await self._remove_routes(app_uid)
        await self._remove_application(app_uid)

    async def reload_app(self, app_uid: str, new_env_data: dict) -> None:
        """Обновляет конфигурацию приложения в unit

        :param app_uid: uid приложения
        :param new_env_data: новая конфигурация
        """

        await self._load_application(app_uid, new_env_data)
        await self._remove_routes(app_uid)
        await self._load_routes(app_uid, new_env_data)

        log_event('app configuration updated', app_uid)


class DevelopmentUnitService(UnitService):
    async def _load_routes(self, app_uid: str, env_data: dict) -> None:
        app_dirpath = os.path.join(settings.MOUNTED_APPS_PATH, app_uid)
        static_path = env_data.get('STATIC_PATH')
        base_routes = [{'action': {'pass': f'applications/{app_uid}'}}]

        if not static_path:
            routes = base_routes
        else:
            absolute_static_path = os.path.join(app_dirpath, static_path)
            static_route = {
                'match': {'uri': '/static/*'},
                'action': {'share': absolute_static_path},
            }
            routes = [static_route, *base_routes]

        route_url = f'{self.BASE_URL}/routes/{app_uid}/'

        await self.client.fetch(route_url, body=json.dumps(routes), method='PUT')

        log_event('registered app routing', app_uid)

    async def _load_listener(self, app_uid: str) -> int:
        app_port = get_unused_port()

        listener_url = f'{self.BASE_URL}/listeners/*:{app_port}/'
        listener_data = {'pass': f'routes/{app_uid}'}

        await self.client.fetch(
            listener_url, body=json.dumps(listener_data), method='PUT'
        )

        log_event('listener registered on port %s', app_uid, app_port)

        return app_port

    @staticmethod
    def _is_deleted_app_listener(deleted_app_uid: str, listener: dict) -> bool:
        request_destination = listener['pass']
        _, app_uid = request_destination.split('/')
        return app_uid == deleted_app_uid

    async def _remove_listener(self, app_uid: str) -> None:
        listeners_url = f'{self.BASE_URL}/listeners/'
        reponse = await self.client.fetch(listeners_url, method='GET')

        response_data = reponse.body.decode()
        listeners = json.loads(response_data)

        is_deleted_app_listener = partial(self._is_deleted_app_listener, app_uid)
        filtered_listeners = {
            address: destination
            for address, destination in listeners.items()
            if not is_deleted_app_listener(destination)
        }

        await self.client.fetch(
            listeners_url,
            body=json.dumps(filtered_listeners),
            method='PUT',
            raise_error=False,
        )

        log_event('unregistered listener', app_uid)

    async def _remove_routes(self, app_uid: str) -> None:
        route_url = f'{self.BASE_URL}/routes/{app_uid}/'
        await self.client.fetch(route_url, method='DELETE', raise_error=False)

        log_event('unregistered route', app_uid)

    async def register_app(self, app_uid: str, environment_data: dict) -> dict:
        await self._load_application(app_uid, environment_data)
        await self._load_routes(app_uid, environment_data)
        app_port = await self._load_listener(app_uid)
        return {'port': app_port}

    async def unregister_app(self, app_uid: str) -> None:
        await self._remove_listener(app_uid)
        await self._remove_routes(app_uid)
        await self._remove_application(app_uid)

    async def reload_app(self, app_uid: str, new_env_data: dict) -> None:
        """Обновляет конфигурацию приложения в unit

        :param app_uid: uid приложения
        :param new_env_data: новая конфигурация
        """

        await self._load_routes(app_uid, new_env_data)
        await self._load_application(app_uid, new_env_data)

        log_event('app configuration updated', app_uid)


def validate_package(package: 'ZipFile', rules: List[dict]) -> None:
    """
    Проверяет zip архив на соответствие условиям. Если хотя бы
    одно не выполняется, выбрасывает соответствующее исключение

    :param package: zip файл.
    :param rules: список правил, по которым валидируется архив.
    Каждое правило состоит из функции-предиката (условия выполнения) и исключения,
    которое вызывается при невыполнении условия
    """

    for rule in rules:
        constraint_is_fulfilled = rule['constraint']
        if not constraint_is_fulfilled(package):
            exception = rule['exception']
            raise exception()


def parse_environment_variables(env_file_path: str) -> dict:
    """Читает env файл приложения и записывает в локальную структуру

    :param env_file_path: путь до файла с переменными окружения
    :return: распарсенные переменные среды
    """

    with open(env_file_path, 'r') as file:
        data = file.read().strip('\n')
        lines = data.split('\n')
        variables = [variable_line.split('=') for variable_line in lines]
        return {name: value for name, value in variables}


def get_app_environment_data(app_uid: str) -> dict:
    """Считывает переменные среды приложения

    :param app_uid: uid приложения
    :return: словарь с переменными среды
    """

    app_path = os.path.join(settings.apps_path, app_uid)
    env_path = os.path.join(app_path, ENV_FILE_NAME)
    return parse_environment_variables(env_path)


def load_app_requirements(app_dir: str) -> None:
    """Создаёт окружение в директории приложения и устанавливает зависимости

    :param app_dir: путь до приложения
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

    :return: путь до созданной директории приложения
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
    после чего устанавливает эти зависимости

    :param package: zip архив с файлами приложения и зависимостей
    :return: id приложения
    """

    app_dir = create_app_directory()
    apps_path, app_uid = path.split(app_dir)

    package.extractall(app_dir)
    load_app_requirements(app_dir)

    log_event('virtual environment created', app_uid)

    return app_uid


def get_unused_port() -> int:
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.bind(('', 0))
        return sock.getsockname()[1]


def destroy_application_environment(app_uid: str) -> None:
    """Удаляет директорию приложения

    :param app_uid: uid приложения
    """

    app_dirpath = path.join(settings.apps_path, app_uid)
    shutil.rmtree(app_dirpath)

    log_event('virtual environment destroyed', app_uid)


async def update_application_environment(app_uid: str, package: 'ZipFile') -> None:
    """Полностью обновляет содержимое приложения,
    переустанавливает зависимости

    :param app_uid: uid приложения, содержимое которого нужно обновить
    :param package: zip архив с новыми файлами приложения и зависимостей
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


def get_unit_service_from_env() -> 'UnitService':
    is_production = settings.ENVIRONMENT == Environment.PRODUCTION
    return ProductionUnitService() if is_production else DevelopmentUnitService()


def create_db_instance(client: 'DockerClient', env_data: dict) -> str:
    db_port = env_data.get('DB_PORT', 5432)
    db_user = env_data.get('DB_USER')
    db_password = env_data.get('DB_PASSWORD')

    postgres_image = client.images.pull('postgres:latest')
    container = client.containers.create(
        image=postgres_image,
        auto_remove=True,
        ports={5432: db_port},
        environment={'POSTGRES_USER': db_user, 'POSTGRES_PASSWORD': db_password},
    )
    container.start()
    return container.id


def destroy_db_instance(client: 'DockerClient', container_id: str) -> None:
    container = client.containers.get(container_id)
    if container:
        container.stop()
