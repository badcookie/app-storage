import logging

from motor.motor_tornado import MotorClient
from server.app import make_app
from server.repository import ApplicationRepository
from server.settings import Environment, settings
from tornado.ioloop import IOLoop


def init_app_options() -> dict:
    db = MotorClient(settings.db_dsn).default
    debug = settings.ENVIRONMENT == Environment.DEVELOPMENT

    return {'repository': ApplicationRepository(db), 'debug': debug}


if __name__ == '__main__':
    options = init_app_options()
    app = make_app(options)

    try:
        app.listen(settings.SERVER_PORT)
        logging.info('Server started on port %s', settings.SERVER_PORT)
        IOLoop.current().start()
    except (KeyboardInterrupt, SystemExit):
        logging.info('Server graceful shutdown')
