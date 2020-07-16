import json
import threading

from flask import Blueprint, make_response, request, jsonify, Response

from app import handler
from app.models import Courses
from app.block_views import get_block_view

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
    payload = request.form.to_dict()
    payload = payload['text'].split(' ')

    course = Courses.query.filter_by(course=payload).first()
    if course is None:
        return make_response("No such course found. Use /courses to see available courses", 200)
    item = get_block_view("courses/course_summary.json")
    item = item.replace("{COURSE NAME}", course.course)
    item = item.replace("{COURSE_SHORT_SUMMARY}", course.msg)
    return Response(item, mimetype='application/json')


@slack.route("/courses", methods=['POST'])
def get_courses_listing():
    response = get_block_view("courses/courses_list.json")
    list_items = []
    for course in Courses.query.all():
        item = get_block_view("courses/course_list_item.json")
        item = item.replace("{COURSE NAME}", course.course)
        course_brief_summary = course.msg if len(course.msg) < 20 else course.msg[0:20]
        item = item.replace("{COURSE_SHORT_SUMMARY}", course_brief_summary)
        list_items.append(item)
    response = response.replace("{ITEM_PLACE_HOLDER}", ",\n".join(list_items))
    return Response(response, mimetype='application/json')


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


@slack.route('/interactions', methods=['POST'])
def interactions():
    """
    The main route for enabling interactions with shortcuts, modals, or interactive
    components (such as buttons, select menus, and datepickers). To add an interaction,
    simply modify the code in the function app.slack_handler.interactions
    """

    # Verify request
    if not verify_request(request):
        return make_response("", 400)

    # Parse request
    payload = json.loads(request.form.to_dict()["payload"])

    # Spawn a thread to service the request
    threading.Thread(target=handler.interactions, args=[payload]).start()
    return make_response("", 200)
