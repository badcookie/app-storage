import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from server.domain import Application
from server.repository import ApplicationRepository
from server.settings import settings


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
async def db_connection(db_service):
    client = AsyncIOMotorClient(settings.DB.DB_HOST, settings.DB.DB_PORT)
    db = client.test_database
    yield db
    await client.drop_database(db)


@pytest.fixture
def repository(db_connection):
    return ApplicationRepository(db_connection)


@pytest.mark.asyncio
async def test_application_repository(repository):
    collection = await repository.list()
    assert isinstance(collection, list) and len(collection) == 0

    first_in_memory_instance = Application(uid='ab9eoy78', port=23976)
    first_instance_id = await repository.add(first_in_memory_instance)
    assert first_instance_id

    first_instance = await repository.get(id=first_instance_id)
    assert isinstance(first_instance, Application)

    assert first_instance.id == first_instance_id
    assert first_instance.port == first_in_memory_instance.port
    assert first_instance.uid == first_in_memory_instance.uid

    non_existing_instance = await repository.get(id=-1)
    assert non_existing_instance is None

    collection = await repository.list()
    assert len(collection) == 1

    found_instance = await repository.get(port=23976)
    assert found_instance.id == first_instance_id

    await repository.delete(id=first_instance_id)

    deleted_instance = await repository.get(id=first_instance_id)
    assert deleted_instance is None
