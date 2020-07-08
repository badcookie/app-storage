import logging
from io import BytesIO
from zipfile import ZipFile

from more_itertools import one
from motor.motor_tornado import MotorClient
from server.repository import ApplicationRepository
from server.services import (
    create_application_environment,
    register_app,
    validate_package,
)
from server.settings import settings as config
from server.validation import VALIDATION_RULES
from tornado.httputil import HTTPServerRequest
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

logger = logging.getLogger('app')


def get_request_file(request: 'HTTPServerRequest') -> 'ZipFile':
    files = request.files
    file_data = one(files.get('zipfile'))
    file_body = file_data['body']
    return ZipFile(BytesIO(file_body), 'r')


class ApplicationsHandler(RequestHandler):
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

        app_data = {'uid': app_uid, 'port': app_port}
        self.write(app_data)


def make_app():
    db = MotorClient().default
    settings = {
        'app_repository': ApplicationRepository(db),
        'db': db,
    }
    return Application([(r'/create/', ApplicationsHandler)], **settings)


if __name__ == '__main__':
    app = make_app()
    try:
        app.listen(config.APP_PORT)
        logging.info(f'Server started on port: {config.APP_PORT}')
        IOLoop.current().start()
    except (KeyboardInterrupt, SystemExit):
        logging.info('Server graceful shutdown')
