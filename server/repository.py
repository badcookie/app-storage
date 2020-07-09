from abc import ABC, abstractmethod
from typing import List, Optional, Type, Union

import shortuuid
from server.domain import ApplicationReadOnly, Entity


class Repository(ABC):
    model: Type['Entity']

    def __init__(self, db):
        self._db = db

    @abstractmethod
    async def add(self, entity: 'Entity') -> Optional[Union[int, str]]:
        ...

    @abstractmethod
    async def get(self, **params) -> 'Entity':
        ...

    @abstractmethod
    async def list(self) -> List['Entity']:
        ...

    @abstractmethod
    async def delete(self, **params) -> None:
        ...


class NoSQLRepository(Repository):
    collection: str

    async def add(self, entity: 'Entity') -> str:
        uuid = shortuuid.uuid()
        entity_data = {**entity.dict(), 'id': uuid}
        await self._db[self.collection].insert_one(entity_data)
        return uuid

    async def get(self, **params) -> 'Entity':
        entity = await self._db[self.collection].find_one(params)
        return self.model(**entity) if entity else None

    async def list(self) -> List['Entity']:
        entities = await self._db[self.collection].find().to_list(length=None)
        return [self.model(**entity) for entity in entities]

    async def delete(self, **params) -> None:
        await self._db[self.collection].delete_one(params)


class ApplicationRepository(NoSQLRepository):
    model = ApplicationReadOnly
    collection = 'applications'
