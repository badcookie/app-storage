import logging
from os import pardir, path

from dotenv import find_dotenv
from pydantic import BaseSettings, Field

env_path = find_dotenv()


class Environment(str):
    DEVELOPMENT = 'development'
    TEST = 'test'
    PRODUCTION = 'production'


class DBSettings(BaseSettings):
    HOST: str = Field(env='DB_HOST')
    PORT: int = Field(env='DB_PORT', default=27017)
    USER: str = Field(env='DB_USER')
    PASSWORD: str = Field(env='DB_PASSWORD')


class Settings(BaseSettings):
    ENVIRONMENT: 'Environment'
    PROJECT_NAME: str

    DB: 'DBSettings' = DBSettings(_env_file=env_path)

    UNIT_PORT: int = 9000
    UNIT_HOST: str = 'localhost'

    SERVER_PORT: int = 8000

    APP_ID_LENGTH: int = 8
    MAX_PACKAGE_SIZE_MB: int = 5
    APP_ID_CREATION_TRIES_COUNT: int = 5

    BASE_DIR: str = path.dirname(path.dirname(path.abspath(__file__)))
    LOCAL_APPS_PATH: str = Field(
        env='APPS_PATH', default=path.abspath(path.join(BASE_DIR, pardir, 'apps'))
    )
    MOUNTED_APPS_PATH: str

    @property
    def logging(self) -> dict:
        return {
            'version': 1,
            'formatters': {
                'simple': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': logging.DEBUG,
                    'formatter': 'simple',
                },
            },
            'loggers': {'': {'level': logging.DEBUG, 'handlers': ['console']}},
        }

    @property
    def apps_path(self):
        return (
            self.LOCAL_APPS_PATH
            if self.ENVIRONMENT == Environment.DEVELOPMENT
            else self.MOUNTED_APPS_PATH
        )


settings = Settings(_env_file=env_path)
