from flask import Flask, request
from utils import parse_query_string

application = Flask(__name__)


@application.route("/very_complex_query", methods=["POST"])
def post_request():
    data = request.environ.get("wsgi.input").read()
    params = parse_query_string(data)
    some_id = params.get("yet_another_id")
    return str(some_id)


@application.route("/", methods=["GET"])
def get_request():
    return "Success"
