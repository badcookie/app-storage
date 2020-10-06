from typing import Optional

from pydantic import BaseModel


class Entity(BaseModel):
    pass


class Application(Entity):
    uid: str
    name: Optional[str]
    description: Optional[str]
    port: Optional[int]
    db_container_id: Optional[str]


class ApplicationReadOnly(Application):
    """Модель для чтения из хранилища"""

    id: str
