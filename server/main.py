import logging.config

from server.app import make_app
from server.services import Services
from server.settings import settings
from tornado.ioloop import IOLoop

logging.config.dictConfig(settings.logging)
logger = logging.getLogger('app')


def init_services() -> 'Services':
    return Services()


if __name__ == '__main__':
    services = init_services()
    app = make_app(services)

    try:
        app.listen(settings.APP_PORT)
        logger.info('Server started on port %s', settings.APP_PORT)
        IOLoop.current().start()
    except (KeyboardInterrupt, SystemExit):
        logger.info('Server graceful shutdown')
