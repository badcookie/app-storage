import json
import logging.config
from io import BytesIO
from os import path
from typing import Optional
from zipfile import ZipFile

from server.domain import Application
from server.errors import (
    APP_NOT_FOUND_MESSAGE,
    FILE_EXPECTED_MESSAGE,
    RESOURCE_ID_EXPECTED_MESSAGE,
    UNEXPECTED_PARAM_MESSAGE,
    handle_internal_error,
)
from server.services import (
    create_application_environment,
    create_db_instance,
    destroy_application_environment,
    destroy_db_instance,
    get_app_environment_data,
    log_event,
    update_application_environment,
    validate_package,
)
from server.settings import settings
from server.validation import (
    APP_DESCRIPTION_VARIABLE_NAME,
    APP_NAME_VARIABLE_NAME,
    VALIDATION_RULES,
)
from tornado import web, websocket
from tornado.websocket import WebSocketClosedError

logger = logging.getLogger(__name__)


def get_db_data(env_data: dict) -> dict:
    return {
        'DB_PORT': env_data.get('DB_PORT', 5432),
        'DB_PASSWORD': env_data.get('DB_PASSWORD'),
        'DB_USER': env_data.get('DB_USER'),
    }


class WebSocketHandler(websocket.WebSocketHandler):
    uid: str

    def open(self, *args: str, **kwargs: str) -> None:
        query_param = self.request.query_arguments.get('client')
        if not query_param:
            return

        client_uid = query_param[0].decode()
        self.uid = client_uid

        self.application.ws_connections.add(self)

    def on_close(self) -> None:
        self.application.ws_connections.remove(self)

    def check_origin(self, origin: str) -> bool:
        return True


class BaseHandler(web.RequestHandler):
    app_uid: Optional[str]
    ws: Optional['WebSocketHandler']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = self.application.settings['repository']
        self.configurator = self.application.settings['configurator']
        self.docker = self.application.settings['docker']

    def set_default_headers(self) -> None:
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header(
            'Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS'
        )
        self.set_header('Access-Control-Allow-Headers', settings.CLIENT_UID_HEADER)

    def options(self, *args, **kwargs):
        self.set_status(200)
        self.finish()

    async def _handle_error(self) -> None:
        if self.app_uid is not None:
            await self.configurator.unregister_app(self.app_uid)
            destroy_application_environment(self.app_uid)

        await self.notify_client('done')

    async def handle_client_error(self, status: int, error: str) -> None:
        await self._handle_error()

        self.set_status(status)
        await self.finish(error)

    async def handle_internal_error(self, error: str) -> None:
        await self._handle_error()

        self.set_status(500)
        await self.finish(error)

    async def notify_client(self, message: str) -> None:
        if not self.ws:
            return

        try:
            await self.ws.write_message(message)
        except WebSocketClosedError:
            log_event('websocket closed')


class ApplicationsHandler(BaseHandler):
    """
    Принимает zip архив приложения, создаёт для него
    окружение, обновляет конфигурацию веб-сервера
    и сохраняет в бд данные о приложении.
    """

    def prepare(self) -> None:
        self.app_uid = None

        client_uid = self.request.headers.get(settings.CLIENT_UID_HEADER)
        found_ws = [
            ws for ws in self.application.ws_connections if ws.uid == client_uid
        ]
        self.ws = found_ws[0] if found_ws else None

    async def get(self, app_id: Optional[str] = None):
        if app_id is None:
            apps = await self.repository.list()
            query_data = [app.dict() for app in apps]
        else:
            app = await self.repository.get(id=app_id)
            self.app_uid = app.uid
            query_data = app.dict()

        if query_data is None:
            raise web.HTTPError(404, reason=APP_NOT_FOUND_MESSAGE)

        result = json.dumps(query_data)
        return self.write(result)

    def _get_request_file(self) -> Optional['ZipFile']:
        files = self.request.files
        file_data = files.get('zipfile')

        if not file_data:
            return None

        file_body = file_data[0].get('body')

        if file_body is None:
            return None

        return ZipFile(BytesIO(file_body), 'r')

    def _get_db_option(self) -> bool:
        request_data = self.request.body_arguments.get('options')

        if not request_data:
            return False

        decoded_options = request_data[0].decode()
        options = json.loads(decoded_options)

        create_db = options.get('createDb', False)
        return create_db

    @handle_internal_error
    async def post(self, param=None):
        if param is not None:
            raise web.HTTPError(400, reason=UNEXPECTED_PARAM_MESSAGE)

        file = self._get_request_file()

        if not file:
            raise web.HTTPError(400, reason=FILE_EXPECTED_MESSAGE)

        validate_package(file, VALIDATION_RULES)

        await self.notify_client('Creating application environment')

        self.app_uid = create_application_environment(file)
        environment_variables = get_app_environment_data(self.app_uid)

        app_meta = {}

        create_db = self._get_db_option()
        if create_db:
            db_data = get_db_data(environment_variables)

            await self.notify_client('Creating db instance')

            container_id = create_db_instance(self.docker, db_data)
            app_meta.update(db_container_id=container_id)

        await self.notify_client('Registering app configuration')

        result_data = await self.configurator.register_app(
            self.app_uid, environment_variables
        )
        app_meta.update(**(result_data or {}))

        app_name = environment_variables.get(APP_NAME_VARIABLE_NAME)
        app_description = environment_variables.get(APP_DESCRIPTION_VARIABLE_NAME)

        app = Application(
            uid=self.app_uid, name=app_name, description=app_description, **app_meta
        )
        app_id = await self.repository.add(app)

        await self.notify_client('done')

        app_data = {'id': app_id, **app.dict()}

        self.set_status(201)
        self.write(app_data)

    @handle_internal_error
    async def put(self, app_id: str = None):
        if app_id is None:
            raise web.HTTPError(400, reason=RESOURCE_ID_EXPECTED_MESSAGE)

        file = self._get_request_file()

        if not file:
            raise web.HTTPError(400, reason=FILE_EXPECTED_MESSAGE)

        app_to_update = await self.repository.get(id=app_id)

        if app_to_update is None:
            raise web.HTTPError(404, reason=APP_NOT_FOUND_MESSAGE)

        self.app_uid = app_to_update.uid

        await self.notify_client('Updating application environment')

        await update_application_environment(app_to_update.uid, file)
        environment_variables = get_app_environment_data(self.app_uid)

        await self.notify_client('Reloading app configuration')

        await self.configurator.reload_app(self.app_uid, environment_variables)

        data_to_update = {
            'name': environment_variables.get(APP_NAME_VARIABLE_NAME),
            'description': environment_variables.get(APP_DESCRIPTION_VARIABLE_NAME),
        }
        updated_app = await self.repository.update(app_id, data_to_update)

        await self.notify_client('done')

        self.set_status(200)
        self.write(updated_app.dict())

    @handle_internal_error
    async def delete(self, app_id: str = None):
        if app_id is None:
            raise web.HTTPError(400, reason=RESOURCE_ID_EXPECTED_MESSAGE)

        app_to_delete = await self.repository.get(id=app_id)

        if app_to_delete is None:
            raise web.HTTPError(404, reason=APP_NOT_FOUND_MESSAGE)

        uid = app_to_delete.uid

        if app_to_delete.db_container_id is not None:
            await self.notify_client('Destroying db instance')

            destroy_db_instance(self.docker, app_to_delete.db_container_id)

        await self.notify_client('Unregistering app configuration')

        await self.configurator.unregister_app(uid)

        await self.notify_client('Destroying app environment')

        destroy_application_environment(uid)
        await self.repository.delete(id=app_id)

        await self.notify_client('done')

        self.set_status(204)


class AppStorageApplication(web.Application):
    ws_connections = set()


def make_app(options) -> 'AppStorageApplication':
    static_path = path.join(settings.BASE_DIR, 'client', 'build', 'static')
    template_path = path.join(settings.BASE_DIR, 'client', 'build')

    logging.config.dictConfig(settings.logging)

    routes = [
        (r'/applications/', ApplicationsHandler),
        (r'/applications/([^/]+)/?', ApplicationsHandler),
        (r'/ws/', WebSocketHandler),
    ]

    return AppStorageApplication(
        routes, static_path=static_path, template_path=template_path, **options,
    )
