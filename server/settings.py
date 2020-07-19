import logging
from os import pardir, path

from dotenv import find_dotenv
from pydantic import BaseSettings

env_path = find_dotenv()


class Environment(str):
    DEVELOPMENT = 'development'
    TEST = 'test'
    PRODUCTION = 'production'


class DBSettings(BaseSettings):
    HOST: str
    PORT: int = 27017
    USER_: str
    PASSWORD: str


class Settings(BaseSettings):
    ENVIRONMENT: 'Environment'
    PROJECT_NAME: str = 'app_storage'
    APP_PORT: int = 8000
    UNIT_PORT: int = 9000
    UNIT_HOST: str = '127.0.0.1'
    DB: 'DBSettings'
    APP_ID_LENGTH: int = 8
    MAX_PACKAGE_SIZE_MB: int = 5
    APP_ID_CREATION_TRIES_COUNT: int = 5
    BASE_DIR: str = path.dirname(path.dirname(path.abspath(__file__)))
    APPS_DIR: str = path.abspath(path.join(BASE_DIR, pardir, 'apps'))

    @property
    def logging_config(self):
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


settings = Settings(_env_file=env_path)
