import os
import shutil
from zipfile import ZipFile

import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from server.app import make_app
from server.settings import settings
from server.validation import VALIDATION_RULES


@pytest.fixture
def validation_rules():
    return VALIDATION_RULES


@pytest.fixture
async def db_connection():
    client = AsyncIOMotorClient(host=settings.DB.DB_HOST, port=settings.DB.DB_PORT)
    db = client.test
    yield db
    await client.drop_database(db)


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
