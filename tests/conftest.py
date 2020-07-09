import os
import shutil
from zipfile import ZipFile

import docker
import pytest
from server.app import make_app
from server.settings import settings
from server.validation import VALIDATION_RULES


@pytest.fixture
def validation_rules():
    return VALIDATION_RULES


@pytest.fixture(scope='session')
def docker_client():
    return docker.from_env()


@pytest.fixture()
def unit_service(docker_client):
    image = docker_client.images.pull(settings.UNIT_IMAGE)
    volume = {settings.APPS_DIR: {'bind': '/apps/', 'mode': 'rw'}}
    command = f'unitd --no-daemon --control 127.0.0.1:{settings.UNIT_PORT}'

    container = docker_client.containers.create(
        image=image,
        network='host',
        command=command,
        volumes=volume,
        name='test_unit_service',
        auto_remove=True,
    )
    container.start()
    yield container
    container.stop()


@pytest.fixture()
def db_service(docker_client):
    image = docker_client.images.pull(settings.DB_IMAGE)
    container = docker_client.containers.create(
        image=image, network='host', name='test_db_service', auto_remove=True,
    )
    container.start()
    yield container
    container.stop()


@pytest.fixture
def get_package():
    cache = {}

    def getter(package_name: str) -> 'ZipFile':
        fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', package_name)
        package_path = shutil.make_archive(fixture_path, 'zip', fixture_path)
        package = ZipFile(package_path)
        cache[package_path] = package
        return package

    yield getter

    (package_dir,) = cache
    cache[package_dir].close()
    os.remove(package_dir)


@pytest.fixture(scope='session', autouse=True)
def create_apps_directory():
    yield os.mkdir(settings.APPS_DIR)
    shutil.rmtree(settings.APPS_DIR)


@pytest.fixture
def get_items_generator():
    def getter(collection):
        for item in collection:
            yield item

    return getter


@pytest.fixture
def app():
    return make_app()
