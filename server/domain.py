from typing import Optional

from pydantic import BaseModel


class Entity(BaseModel):
    pass


class Application(Entity):
    uid: str
    port: int
    name: Optional[str]
    description: Optional[str]


class ApplicationReadOnly(Application):
    """Модель для чтения из хранилища"""

    id: str
