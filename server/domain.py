from pydantic import BaseModel


class Entity(BaseModel):
    pass


class Application(Entity):
    uid: str
    port: int


class ApplicationReadOnly(Entity):
    id: int
