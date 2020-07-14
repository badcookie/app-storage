import logging.config
from io import BytesIO
from os import path
from zipfile import ZipFile

from more_itertools import one
from motor.motor_tornado import MotorClient
from server.domain import Application
from server.repository import ApplicationRepository
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
from tornado.ioloop import IOLoop

logging.config.dictConfig(config.logging_config)
logger = logging.getLogger('app')


def get_request_file(request: 'HTTPServerRequest') -> 'ZipFile':
    files = request.files
    file_data = one(files.get('zipfile'))
    file_body = file_data['body']
    return ZipFile(BytesIO(file_body), 'r')


# class IndexHandler(web.RequestHandler):
#     async def get(self):
#         return self.render('index.html')


class BaseHandler(web.RequestHandler):
    def set_default_headers(self) -> None:
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', 'x-requested-with')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def options(self):
        self.set_status(204)
        self.finish()


class ApplicationHandler(BaseHandler):
    """
    Принимает zip архив приложения, создаёт для него
    окружение, обновляет конфигурацию веб-сервера
    и сохраняет в бд данные о приложении.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = self.application.settings['app_repository']

    async def post(self, param):
        if param is not None:
            raise web.HTTPError(400)

        file = get_request_file(self.request)
        validate_package(file, VALIDATION_RULES)

        app_uid = create_application_environment(file)
        app_port = await register_app(app_uid)

        app_instance = Application(uid=app_uid, port=app_port)
        app_id = await self.repository.add(app_instance)

        app_data = {'uid': app_uid, 'port': app_port, 'id': app_id}
        self.set_status(201)
        self.write(app_data)

    async def delete(self, app_id: str):
        app_to_delete = await self.repository.get(id=app_id)

        if app_to_delete is None:
            raise web.HTTPError(404)

        uid = app_to_delete.uid
        port = app_to_delete.port

        await unregister_app(uid, port)
        destroy_application_environment(uid)
        await self.repository.delete(id=app_id)

        self.set_status(204)


def make_app():
    db = MotorClient().default
    settings = {'app_repository': ApplicationRepository(db), 'db': db}

    static_path = path.join(config.BASE_DIR, 'client', 'build', 'static')
    template_path = path.join(config.BASE_DIR, 'client', 'build')

    debug = config.ENVIRONMENT == Environment.DEVELOPMENT

    routes = [
        # (r'/', IndexHandler),
        (r'/application/([^/]+)?', ApplicationHandler),
    ]

    return web.Application(
        routes,
        static_path=static_path,
        template_path=template_path,
        debug=debug,
        **settings,
    )


if __name__ == '__main__':
    app = make_app()

    try:
        app.listen(config.APP_PORT)
        logger.info('Server started on port %s', config.APP_PORT)
        IOLoop.current().start()
    except (KeyboardInterrupt, SystemExit):
        logger.info('Server graceful shutdown')
