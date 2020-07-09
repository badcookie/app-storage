import logging
from io import BytesIO
from zipfile import ZipFile

from more_itertools import one
from motor.motor_tornado import MotorClient
from server.domain import Application
from server.repository import ApplicationRepository
from server.services import (
    create_application_environment,
    register_app,
    validate_package,
)
from server.settings import settings as config
from server.validation import VALIDATION_RULES
from tornado import web
from tornado.httputil import HTTPServerRequest
from tornado.ioloop import IOLoop

logger = logging.getLogger('app')


def get_request_file(request: 'HTTPServerRequest') -> 'ZipFile':
    files = request.files
    file_data = one(files.get('zipfile'))
    file_body = file_data['body']
    return ZipFile(BytesIO(file_body), 'r')


class ApplicationsHandler(web.RequestHandler):
    """
    Принимает zip архив приложения, создаёт для него
    окружение, обновляет конфигурацию веб-сервера
    и сохраняет в бд данные о приложении.
    """

    async def post(self):
        file = get_request_file(self.request)
        validate_package(file, VALIDATION_RULES)

        app_uid = create_application_environment(file)
        app_port = await register_app(app_uid)

        app_repo = self.application.settings['app_repository']
        app_instance = Application(uid=app_uid, port=app_port)
        app_id = await app_repo.add(app_instance)

        app_data = {'uid': app_uid, 'port': app_port, 'id': app_id}
        self.write(app_data)


def make_app():
    db = MotorClient().default
    settings = {
        'app_repository': ApplicationRepository(db),
        'db': db,
    }
    return web.Application([(r'/create/', ApplicationsHandler)], **settings)


if __name__ == '__main__':
    app = make_app()
    try:
        app.listen(config.APP_PORT)
        logging.info(f'Server started on port: {config.APP_PORT}')
        IOLoop.current().start()
    except (KeyboardInterrupt, SystemExit):
        logging.info('Server graceful shutdown')
