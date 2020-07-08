from os import pardir, path

from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = 'app_storage'
    APP_PORT: int = 8000
    UNIT_PORT: int = 9000
    UNIT_HOST: str = '127.0.0.1'
    UNIT_IMAGE: str = 'nginx/unit:1.15.0-python3.7'
    APP_ID_LENGTH: int = 8
    MAX_PACKAGE_SIZE_MB: int = 5
    APP_ID_CREATION_TRIES_COUNT: int = 5
    BASE_DIR: str = path.abspath(path.join(pardir))
    APPS_DIR: str = path.abspath(path.join(BASE_DIR, pardir, 'apps'))


settings = Settings()
