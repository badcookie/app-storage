import os

from flask import Flask

application = Flask(__name__)


@application.route('/', methods=['GET'])
def hello_world():
    return os.getenv('TEST_ENV', 1)


@application.route('/books/<int:book_id>/', methods=['GET', 'DELETE'])
def some_handler(book_id):
    return book_id
