from os import path, pardir

APP_ID_LENGTH = 8
MAX_PACKAGE_SIZE_MB = 5
APP_ID_CREATION_TRIES_COUNT = 5

BASE_DIR = path.abspath(path.join(pardir, pardir))
APPS_DIR = path.abspath(path.join(BASE_DIR, 'apps'))
