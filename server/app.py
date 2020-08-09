import json
import logging
from io import BytesIO
from os import path
from typing import TYPE_CHECKING
from zipfile import ZipFile

from more_itertools import one
from server.domain import Application
from server.services import (
    create_application_environment,
    destroy_application_environment,
    register_app,
    unregister_app,
    validate_package,
)
from server.settings import Environment, settings as config
from server.validation import VALIDATION_RULES
from tornado import web
from tornado.httputil import HTTPServerRequest

if TYPE_CHECKING:
    from server.services import Services


logger = logging.getLogger(__name__)


def get_request_file(request: 'HTTPServerRequest') -> 'ZipFile':
    files = request.files
    file_data = one(files.get('zipfile'))
    file_body = file_data['body']
    return ZipFile(BytesIO(file_body), 'r')


class BaseHandler(web.RequestHandler):
    def set_default_headers(self) -> None:
        super().set_default_headers()
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def options(self):
        self.set_status(204)
        self.finish()


class IndexHandler(BaseHandler):
    async def get(self):
        return self.render('index.html')


class ApplicationHandler(BaseHandler):
    """
    Принимает zip архив приложения, создаёт для него
    окружение, обновляет конфигурацию веб-сервера
    и сохраняет в бд данные о приложении.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.services = self.application.settings['services']

    async def get(self, param):
        repository = self.services.repository
        query_data = (
            await repository.list() if param is None else await repository.get(id=param)
        )

        if query_data is None:
            raise web.HTTPError(404)

        if param is None:
            fake_apps = [
                {'id': 1, 'port': 1234, 'uid': 'abc'},
                {'id': 2, 'port': 1499, 'uid': 'def'},
            ]
            query_data.extend(fake_apps)

        result = json.dumps(query_data)
        return self.write(result)

    async def post(self, param):
        if param is not None:
            raise web.HTTPError(400)

        file = get_request_file(self.request)
        validate_package(file, VALIDATION_RULES)

        app_uid = create_application_environment(file)
        app_port = await register_app(app_uid)

        app = Application(uid=app_uid, port=app_port)
        app_id = await self.services.repository.add(app)

        app_data = {'id': app_id, 'port': app_port, 'uid': app_uid}
        self.set_status(201)
        self.write(app_data)

    async def delete(self, app_id: str):
        app_to_delete = await self.services.repository.get(id=app_id)

        if app_to_delete is None:
            raise web.HTTPError(404)

        uid = app_to_delete.uid
        port = app_to_delete.port

        await unregister_app(uid, port)
        destroy_application_environment(uid)
        await self.services.repository.delete(id=app_id)

        self.set_status(204)


def make_app(services: 'Services') -> 'web.Application':
    static_path = path.join(config.BASE_DIR, 'client', 'build', 'static')
    template_path = path.join(config.BASE_DIR, 'client', 'build')

    debug = config.ENVIRONMENT == Environment.DEVELOPMENT

    routes = [
        (r'/', IndexHandler),
        (r'/applications/([^/]+)?', ApplicationHandler),
    ]

    return web.Application(
        routes,
        static_path=static_path,
        template_path=template_path,
        debug=debug,
        services=services,
    )
