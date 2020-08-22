import os
import shutil
from typing import TYPE_CHECKING, List, Optional, Union
from uuid import uuid4
from zipfile import ZipFile

import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from server.app import make_app
from server.domain import ApplicationReadOnly
from server.repository import Repository
from server.settings import settings
from server.validation import VALIDATION_RULES

if TYPE_CHECKING:
    from server.domain import Entity


@pytest.fixture
def validation_rules():
    return VALIDATION_RULES


@pytest.fixture
async def db_connection():
    client = AsyncIOMotorClient(settings.DB.dsn)
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
def teardown_apps():
    yield
    for root, dirs, files in os.walk(settings.apps_path):
        for directory in dirs:
            app_path = os.path.join(root, directory)
            shutil.rmtree(app_path)


@pytest.fixture
def get_items_generator():
    def getter(collection):
        for item in collection:
            yield item

    return getter


class TestRepository(Repository):
    model = ApplicationReadOnly

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def add(self, entity: 'Entity') -> Optional[Union[int, str]]:
        serialized_entity = entity.dict()
        entity_id = uuid4().hex

        entity_to_save = {**serialized_entity, 'id': entity_id}
        self._db.append(entity_to_save)

        return entity_id

    async def list(self) -> List['Entity']:
        return [self.model(**entity) for entity in self._db]

    async def get(self, **params) -> 'Entity':
        entity = [item for item in self._db if params.items() <= item.items()]
        return self.model(**entity[0]) if entity else None

    async def delete(self, **params) -> None:
        self._db = [item for item in self._db if not params.items() <= item.items()]


def init_app_options():
    db = []
    return {'repository': TestRepository(db)}


@pytest.fixture
def app():
    options = init_app_options()
    return make_app(options)
