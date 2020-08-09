import logging.config

from motor.motor_tornado import MotorClient
from server.app import make_app
from server.repository import ApplicationRepository
from server.services import Services
from server.settings import settings
from tornado.ioloop import IOLoop

logging.config.dictConfig(settings.logging)
logger = logging.getLogger('app')


def init_services() -> 'Services':
    db = MotorClient().default
    repository = ApplicationRepository(db)
    return Services(repository)


if __name__ == '__main__':
    services = init_services()
    app = make_app(services)

    try:
        app.listen(settings.APP_PORT)
        logger.info('Server started on port %s', settings.APP_PORT)
        IOLoop.current().start()
    except (KeyboardInterrupt, SystemExit):
        logger.info('Server graceful shutdown')
