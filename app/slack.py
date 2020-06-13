from flask import Blueprint, make_response, request

from app.slack_utils import verify_request
from config import Config

slack = Blueprint(
    'slack', __name__,
)


@slack.route('/pair', methods=['POST'])
def pair():
    if not verify_request(request):
        return make_response("", 400)
    return make_response("Pair success", 200)
