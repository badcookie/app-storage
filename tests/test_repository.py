import pytest
from server.domain import Application
from server.repository import ApplicationRepository


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

    assert first_instance.name is None
    assert first_instance.description is None

    non_existing_instance = await repository.get(id=-1)
    assert non_existing_instance is None

    collection = await repository.list()
    assert len(collection) == 1

    found_instance = await repository.get(port=23976)
    assert found_instance.id == first_instance_id

    data_to_update = {'name': 'Bob', 'description': 'Nice app'}
    updated_instance = await repository.update(first_instance_id, data_to_update)

    assert updated_instance.name == data_to_update['name']
    assert updated_instance.description == data_to_update['description']

    await repository.delete(id=first_instance_id)

    deleted_instance = await repository.get(id=first_instance_id)
    assert deleted_instance is None
