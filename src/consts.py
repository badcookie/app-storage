from os import environ, pardir, path

APP_ID_LENGTH = 8
MAX_PACKAGE_SIZE_MB = 5
APP_ID_CREATION_TRIES_COUNT = 5

APP_PORT = environ.get("APP_PORT", 8000)
UNIT_PORT = environ.get("UNIT_PORT", 9000)
UNIT_IMAGE = environ.get("UNIT_IMAGE", "nginx/unit:1.15.0-python3.7")
PROJECT_NAME = environ.get("PROJECT_NAME", "app_storage")

BASE_DIR = path.abspath(path.join(pardir))
APPS_DIR = path.abspath(path.join(BASE_DIR, pardir, "apps"))
