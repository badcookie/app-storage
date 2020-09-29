import logging
from os import pardir, path

from dotenv import find_dotenv
from pydantic import BaseSettings, Field

env_path = find_dotenv()


class Environment(str):
    DEVELOPMENT = 'development'
    TEST = 'test'
    PRODUCTION = 'production'


class AppFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'app_uid'):
            record.app_uid = '-'
        return True


class DBSettings(BaseSettings):
    HOST: str = Field(env='DB_HOST')
    PORT: int = Field(env='DB_PORT', default=27017)
    USER: str = Field(env='DB_USER')
    PASSWORD: str = Field(env='DB_PASSWORD')

    @property
    def dsn(self):
        return ''.join(
            ['mongodb://', f'{self.USER}:{self.PASSWORD}', f'@{self.HOST}:{self.PORT}']
        )


class Settings(BaseSettings):
    ENVIRONMENT: 'Environment'
    PROJECT_NAME: str
    PROJECT_ADDRESS: str

    DB: 'DBSettings' = DBSettings(_env_file=env_path)

    UNIT_PORT: int = 9000
    UNIT_HOST: str = 'localhost'

    SERVER_PORT: int = 8000

    APP_ID_LENGTH: int = 8
    MAX_PACKAGE_SIZE_MB: int = 8
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
                    'format': '%(asctime)s - %(levelname)s - %(app_uid)s - %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': logging.DEBUG,
                    'formatter': 'simple',
                },
            },
            'filters': {'app_filter': {'()': 'server.settings.AppFilter'}},
            'loggers': {
                '': {
                    'level': logging.DEBUG,
                    'handlers': ['console'],
                    'filters': ['app_filter'],
                }
            },
        }

    @property
    def apps_path(self):
        return (
            self.LOCAL_APPS_PATH
            if self.ENVIRONMENT == Environment.DEVELOPMENT
            else self.MOUNTED_APPS_PATH
        )


settings = Settings(_env_file=env_path)
