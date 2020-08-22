import logging.config

from motor.motor_tornado import MotorClient
from server.app import make_app
from server.repository import ApplicationRepository
from server.settings import Environment, settings
from tornado.ioloop import IOLoop

logging.config.dictConfig(settings.logging)
logger = logging.getLogger('app')


def init_app_options() -> dict:
    dsn = ''.join(
        [
            'mongodb://',
            f'{settings.DB.USER}:{settings.DB.PASSWORD}',
            f'@{settings.DB.HOST}:{settings.DB.PORT}',
        ]
    )
    db = MotorClient(dsn).default
    debug = settings.ENVIRONMENT == Environment.DEVELOPMENT

    return {'repository': ApplicationRepository(db), 'debug': debug}


if __name__ == '__main__':
    options = init_app_options()
    app = make_app(options)

    try:
        app.listen(settings.APP_PORT)
        logger.info('Server started on port %s', settings.APP_PORT)
        IOLoop.current().start()
    except (KeyboardInterrupt, SystemExit):
        logger.info('Server graceful shutdown')
