from os import path, pardir

APP_ID_LENGTH = 8
MAX_PACKAGE_SIZE_MB = 5
BASE_DIR = path.abspath(path.join(pardir, pardir))
BASE_VENV_DIR = path.abspath(path.join(pardir, pardir, 'venv'))

DEFAULT_APPS_BASE_DIR = path.abspath(path.join(BASE_DIR, 'src', 'tests', 'apps'))
