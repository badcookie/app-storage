import json

from flask import Flask, request

application = Flask(__name__)


@application.route('/some_path', methods=['POST'])
def hello_world():
    data = request.environ.get('wsgi.input').read()
    some_id = json.loads(data).get('some_id')
    return f'{some_id + 1}\n'
