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

    print(request.get_data())
    payload = request.form.to_dict()
    payload = payload['text'].split(' ')
    print(payload)

    return make_response("Pair success", 200)


@slack.route("/course", methods=['POST'])
def get_course_summary():
    return make_response("Course Summary", 200)


@slack.route("/courses", methods=['POST'])
def get_courses_listing():
    pass


@slack.route('/stylecheck', methods=['POST'])
def stylecheck():
    if not verify_request(request):
        return make_response("", 400)

    print(request.get_data())
    payload = request.form.to_dict()
    print(payload)
    payload = payload['text'].split(' ')
    print(payload)

    return make_response("Pair success", 200)
