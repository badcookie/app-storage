from pydantic import BaseModel


class Entity(BaseModel):
    pass


class Application(Entity):
    uid: str
    port: int


class ApplicationReadOnly(Application):
    """Модель для чтения из хранилища"""

    id: str
