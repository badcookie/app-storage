import logging

from motor.motor_tornado import MotorClient
from server.app import make_app
from server.repository import ApplicationRepository
from server.services import get_unit_service_from_env
from server.settings import Environment, settings
from tornado.ioloop import IOLoop


def init_app_options() -> dict:
    db = MotorClient(settings.DB.dsn).default
    debug = settings.ENVIRONMENT == Environment.DEVELOPMENT
    configurator = get_unit_service_from_env()

    return {
        'debug': debug,
        'repository': ApplicationRepository(db),
        'configurator': configurator,
    }


if __name__ == '__main__':
    options = init_app_options()
    app = make_app(options)

    try:
        app.listen(settings.SERVER_PORT)
        logging.info('Server started on port %s', settings.SERVER_PORT)
        IOLoop.current().start()
    except (KeyboardInterrupt, SystemExit):
        logging.info('Server graceful shutdown')
