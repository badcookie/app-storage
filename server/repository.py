from abc import ABC, abstractmethod
from typing import List, Optional, Type

from server.domain import ApplicationReadOnly, Entity


class Repository(ABC):
    model: Type['Entity']

    def __init__(self, db):
        self._db = db

    @abstractmethod
    async def add(self, entity: 'Entity') -> Optional[int]:
        ...

    @abstractmethod
    async def get(self, **params) -> 'Entity':
        ...

    @abstractmethod
    async def list(self) -> List['Entity']:
        ...


class NoSQLRepository(Repository):
    collection: str

    async def add(self, entity: 'Entity') -> int:
        entity_data = entity.dict()
        result = await self._db[self.collection].insert_one(entity_data)
        return result.inserted_id

    async def get(self, **params) -> 'Entity':
        if 'id' in params:
            entity_id = params.pop('id')
            params['_id'] = entity_id
        entity = await self._db[self.collection].find_one(params)
        return self.model(**entity) if entity else None

    async def list(self) -> List['Entity']:
        entities = await self._db[self.collection].find({})
        return [self.model(**entity) for entity in entities]


class ApplicationRepository(NoSQLRepository):
    model = ApplicationReadOnly
    collection = 'applications'
