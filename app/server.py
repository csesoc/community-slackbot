# Accepts user requests, parses them, and calls the required handler


from app import slack_events_adapter, client, handler, app
from config import Config
from app.event_handlers.stylecheck import handle_style_check_request
from flask import Blueprint, make_response, request, jsonify, Response
from app.models import Courses, UserRoles, Report
from app.block_views import get_block_view
from app.utils import verify_request, retrieve_highest_permission_level, get_role_title

import app.utils as utils
import requests
import hmac
import os
import hashlib
import json
import random
import threading

from app.handler import reply_mention, reply_im, help_modal, trivia_modal, review_modal, review_modal_course, karma_message
from app.jtrivia import init_trivia, trivia_set_channel, trivia_set_qs, trivia_q_number, trivia_player_list, \
    trivia_finalise, trivia_failure, start_trivia, trivia_reply, trivia_response, trivia_customs, \
    trivia_custom_questions
from app.jreview import review_init, review_overall, review_difficulty, review_time, review_submit, review_course
from app.jescape import init_escape, get_view, remove_escape, update_escape, escape_modal

slack_token = Config.SLACK_BOT_TOKEN
slack = Blueprint(
    'slack', __name__,
)


@slack_events_adapter.on("message")
def reply(event_data):
    channel = event_data["event"]["channel"]
    if event_data['token'] != slack_token and 'text' in event_data['event']:
        if event_data['event']['text'].startswith("stylecheck"):
            handle_style_check_request(client, slack_token, event_data)

        # message was edited/deleted
    if "user" not in event_data["event"]:
        return
    user = event_data["event"]["user"]
    channel = event_data["event"]["channel"]
    # wont respond to bots
    if 'bot_id' not in event_data['event'] and 'text' in event_data['event']:
        message = event_data['event']['text']
        reply_im(user, channel, message)


@slack_events_adapter.on("reaction_added")
def slack_emoji(event_data):
    if (event_data['event']['reaction'] != 'karma'):
        return
    utils.add_karma(event_data['event']['item_user'])


@slack_events_adapter.on("reaction_removed")
def slack_emoji_remove(event_data):
    if (event_data['event']['reaction'] != 'karma'):
        return
    utils.remove_karma(event_data['event']['item_user'])


@slack.route('/pair', methods=['POST'])
def pair():
    if not verify_request(request):
        return make_response("", 400)

    payload = request.form.to_dict()
    if retrieve_highest_permission_level(payload["user_id"]) < UserRoles.MOD:
        min_title = get_role_title(UserRoles.MOD)
        return make_response("You do not have permission to run /pair."
                             " You require at least {} privileges to run /pair".format(min_title), 200)
    member_ids = client.conversations_members(channel=payload["channel_id"])["members"]

    groupings = []
    current_group = []
    for member_id in member_ids:
        current_group.append(member_id)
        if len(current_group) == app.config["PAIR_GROUP_SIZE"]:
            groupings.append(current_group)
            current_group = []
    if len(current_group) > 0:
        index = -1 if len(groupings) > 0 else 0
        groupings[index].extend(current_group)

    message = "Pairing Success Groups are:\n\n"

    for i, group in enumerate(groupings):
        message += "Group {}:\n".format(i + 1)
        message += "\n".join(group)
        message += "\n\n"

    return make_response(message, 200)


@slack.route("/course", methods=['POST'])
def get_course_summary():
    # TODO: Add in prerequsities, corresponding term date + lecturer, and display corresponding reviews made via /review
    # TODO: Add in a multi-select menu of courses if course argument is omitted 
    payload = request.form.to_dict()
    payload = payload['text'].split(' ')

    course = Courses.query.filter_by(course=payload).first()
    if course is None:
        return make_response("No such course found. Use /courses to see available courses", 200)
    item = get_block_view("views/courses/course_summary.json")
    item = item.replace("{COURSE NAME}", course.course)
    item = item.replace("{COURSE_SHORT_SUMMARY}", course.msg)
    return Response(item, mimetype='application/json')


@slack.route("/courses", methods=['POST'])
def get_courses_listing():
    response = get_block_view("views/courses/courses_list.json")
    list_items = []
    for course in Courses.query.all():
        item = get_block_view("views/courses/course_list_item.json")
        item = item.replace("{COURSE NAME}", course.course)
        course_brief_summary = course.msg if len(course.msg) < 120 else course.msg[0:120] + "..."
        item = item.replace("{COURSE_SHORT_SUMMARY}", course_brief_summary)
        list_items.append(item)
    response = response.replace("{ITEM_PLACE_HOLDER}", ",\n".join(list_items))
    return Response(response, mimetype='application/json')


@slack.route('/reports', methods=['POST'])
def reports():
    if not verify_request(request):
        return make_response("", 400)
    active_reports = Report.query.all()
    reports = []
    for r in active_reports:
        if len(reports) >= 10:
            break
        anon_msg = utils.get_anon_message_from_id(r.msg_id)
        report_entry = get_block_view("views/reports/report_entry.json")
        report_entry = report_entry.replace("{REPORT_ID}", str(r.id))
        report_entry = report_entry.replace("{REPORT_CONTENT}", r.report)
        report_entry = report_entry.replace("{User 1}", anon_msg.user_id)
        report_entry = report_entry.replace("{User 2}", anon_msg.target_id)
        report_entry = report_entry.replace("{REPORTED_AT}",
                                            "No report time" if r.reported_at is None else r.reported_at.strftime(
                                                "%B %d, %Y, %H:%M:%S%z"))
        reports.append(report_entry)
    reports_string = ",".join(reports)
    if len(reports) > 0:
        reports_string += ","
    response = get_block_view("views/reports/report_message.json")
    response = response.replace("{REPORTS}", reports_string)
    response = response.replace("{NUM_REPORTS}", str(len(reports)))
    return Response(response, mimetype='application/json')


@slack.route('/stylecheck', methods=['POST'])
def stylecheck():
    if not verify_request(request):
        return make_response("", 400)

    payload = request.form.to_dict()
    payload = payload['text'].split(' ')

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

    if (payload['type'] == "view_submission" and 'trivia_start_' in payload['view']['callback_id']):
        trigger_id = payload["trigger_id"]
        try:
            game_id = payload['view']['callback_id'].replace('trivia_start_', '')
            trivia_q_number(game_id,
                            int(payload['view']['state']['values']['number_questions']['number_questions']['value']))
            trivia_player_list(game_id,
                               payload['view']['state']['values']['users_playing']['users_playing']['selected_users'])
            if trivia_finalise(game_id, trigger_id):
                try:
                    with app.app_context():
                        resp = jsonify({'response_action': 'push', 'view': trivia_customs(game_id, trigger_id)})
                        resp.headers['Authorization'] = slack_token
                        return resp
                except Exception as err:
                    print(err)
        except:
            trivia_failure(game_id, trigger_id)
        return make_response("", 200)
    elif payload['type'] == "view_submission" and 'custom_questions_' in payload['view']['callback_id']:
        trivia_custom_questions(payload['view']['callback_id'].replace('custom_questions_', ''),
                                payload['view']['state']['values'])
        # can change if we want to be able to go back to the previous modal but this feels cleaner
        with app.app_context():
            resp = jsonify({'response_action': 'clear'})
            resp.headers['Authorization'] = slack_token
            return resp
    elif payload['type'] == 'view_submission' and 'escape_room_' in payload['view']['callback_id']:
        escape_set = payload['view']['callback_id'].replace('escape_room_', '')
        escape_count = int(escape_set.split('_')[0])
        escape_user = escape_set.split('_')[1]
        if escape_count == 2:
            if int(payload['view']['state']['values']['pin_input']['pin_input']['value']) == 1234567:
                escape_count += 1
            else:
                escape_count = "Failure"
        elif escape_count == 4:
            if payload['view']['state']['values']['pin_input']['pin_input']['value'].lower().strip() == "look in the corner":
                escape_count += 1
            else:
                escape_count = "Failure"
        elif escape_count == 7:
            if int(payload['view']['state']['values']['pin_input']['pin_input']['value']) == 6736:
                escape_count += 1
            else:
                escape_count = "Failure"
        elif escape_count == 10:
            if int(payload['view']['state']['values']['pin_input']['pin_input']['value']) == 3:
                escape_count = "Success"
            else:
                escape_count = "Failure"
        else:
            escape_count += 1
        try:
            with app.app_context():
                resp = jsonify({'response_action': 'update', 'view': escape_modal(escape_user, escape_count)})
                resp.headers['Authorization'] = slack_token
                return resp
        except Exception as err:
            print(err)
            return make_response("", 400)
    # print(payload)

    # Spawn a thread to service the request
    threading.Thread(target=handler.interactions, args=[payload]).start()
    return make_response("", 200)


@slack.route('/CSopportunities', methods=['POST'])
def cs_job_opportunities():
    """
    Lets you know about CS job opportunities from indeed
    Usage: /CSopportunities [OPTIONS, page_number=1, query="software internship"]
    """

    # Verify request
    if not utils.verify_request(request):
        return make_response("", 400)

    # Parse request
    payload = request.form.to_dict()
    # Spawn a thread to service the request
    threading.Thread(target=handler.cs_job_opportunities, args=[payload]).start()
    return make_response("", 200)


@slack.route('/purge', methods=['POST'])
def purge():
    """
    Mass delete unwanted messages.
    Usage: /purge <number of messages> [user, time_period, text_snippet]
    """

    # Verify request
    if not utils.verify_request(request):
        return make_response("", 400)

    # Parse request
    payload = request.form.to_dict()

    # Spawn a thread to service the request
    threading.Thread(target=handler.purge, args=[payload]).start()
    return make_response("", 200)


@slack.route('/say', methods=['POST'])
def say():
    """
    Say something as the slackbot.
    Usage: /say message
    """
    # Verify request
    if not utils.verify_request(request):
        return make_response("", 400)

    # Parse request
    payload = request.form.to_dict()

    # Spawn a thread to service the request
    threading.Thread(target=handler.say, args=[payload]).start()
    return make_response("", 200)


@slack.route('/events', methods=['POST'])
def events():
    """
    Display a list of events using linkup
    Usage: /events <cse | unsw> [page number]
    """
    # Verify request
    if not utils.verify_request(request):
        return make_response("", 400)

    # Parse request
    payload = request.form.to_dict()

    # Spawn a thread to service the request
    threading.Thread(target=handler.events, args=[payload]).start()
    return make_response("", 200)


# Events
@slack_events_adapter.on("team_join")
def team_join(event_data):
    '''
    Onboarding will trigger on both the "team_join" and "app_home_opened" event.
    This is to ensure that new, returning, and existing users of the slack space 
    can easily be onboarded and added to the database without any problems. 
    '''
    # Parse request
    user = event_data["event"]["user"]

    # Spawn a thread to service the request
    threading.Thread(target=handler.onboarding, args=[user]).start()


@slack_events_adapter.on("app_home_opened")
def app_home_opened(event_data):
    """
    See "team_join".
    """
    # Parse request
    event = event_data["event"]
    user = event["user"]
    channel = event["channel"]

    # Spawn a thread to service the request
    threading.Thread(target=handler.onboarding, args=[user, channel]).start()
    threading.Thread(target=handler.app_home, args=[event]).start()


'''@slack.route('/shortcut', methods=['POST'])
def slack_shortcut():
    if not verify_request(request):
        return make_response("",400)
    attributes = json.loads(request.form.get('payload'))
    if attributes['type'] == "shortcut":
        if attributes['callback_id'] == "trivia":
            init_trivia(attributes['trigger_id'], attributes['user']['id'])
    elif attributes['type'] == "block_actions":
        if "trivia_custom_" in attributes['actions'][0]['action_id']:
            trivia_customs(attributes['actions'][0]['action_id'].replace("trivia_custom_", ""), attributes['trigger_id'])
        elif "accept_trivia_" in attributes['actions'][0]['action_id']:
            trivia_reply(attributes['user']['id'], True, attributes['actions'][0]['action_id'].replace("accept_trivia_", ""), attributes['trigger_id'])
        elif "forfeit_trivia_" in attributes['actions'][0]['action_id']:
            trivia_reply(attributes['user']['id'], False, attributes['actions'][0]['action_id'].replace("forfeit_trivia_", ""), attributes['trigger_id'])
        elif "trivia_start_" in attributes['view']['callback_id']:
            if "default_trivia_" in attributes['actions'][0]['action_id']:
                trivia_set_qs(attributes['actions'][0]['action_id'].replace("default_trivia_", ""), attributes['actions'][0]['selected_option']['value'] == "true")
            elif "trivia_channel_" in attributes['actions'][0]['action_id']:
                trivia_set_channel(attributes['actions'][0]['action_id'].replace("trivia_channel_", ""), attributes['actions'][0]['selected_channel'])
        elif "trivia_question_" in attributes['view']['callback_id']:
            trivia_response(attributes['user']['id'], attributes['actions'][0]['value'] == 'correct', attributes['trigger_id'])
    elif attributes['type'] == "view_submission":
        if 'trivia_start_' in  attributes['view']['callback_id']:
            try:
                game_id = attributes['view']['callback_id'].replace('trivia_start_', '')
                trivia_q_number(game_id, int(attributes['view']['state']['values']['number_questions']['number_questions']['value']))
                trivia_player_list(game_id, attributes['view']['state']['values']['users_playing']['users_playing']['selected_users'])
                if trivia_finalise(game_id, attributes['trigger_id']):
                    resp = jsonify({'response_action': 'push', 'view': trivia_customs(game_id, attributes['trigger_id'])})
                    resp.headers['Authorization'] = slack_token
                    return resp
            except:
                trivia_failure(game_id, attributes['trigger_id'])
        elif 'custom_questions_' in attributes['view']['callback_id']:
            trivia_custom_questions(attributes['view']['callback_id'].replace('custom_questions_', ''), attributes['view']['state']['values'])

    return Response()'''


@slack_events_adapter.on("app_mention")
def slack_mention(event_data):
    user = event_data['event']['user']
    channel = event_data["event"]["channel"]
    reply_mention(user, channel)


@slack.route('/helpme', methods=['POST'])
def slack_help():
    if not verify_request(request):
        return make_response("", 400)
    help_modal(request.form.get('trigger_id'), request.form.get('user_id'))
    return make_response("", 200)


@app.route('/review', methods=['POST'])
def slack_review():
    if not verify_request(request):
        return make_response("", 400)
    # TODO: verify that the course given is valid
    # TODO: normalise the course argument e.g. math3611 -> MATH3611, mAth3611 -> MATH3611
    # TODO: add in a multi-select menu feature to the review modal if a course argument is omitted
    if request.form.get('text') != "":
        review_init(request.form.get('user_id'))
        review_course(request.form.get('user_id'), request.form.get('text'))
        review_modal(request.form.get('trigger_id'), request.form.get('text'), request.form.get('user_id'))
    else:
        review_init(request.form.get('user_id'))
        review_modal_course(request.form.get('trigger_id'), request.form.get('user_id'))
    return make_response("", 200)


@app.route('/karma', methods=['POST'])
def slack_karma():
    if not verify_request(request):
        return make_response("", 400)
    karma_message(request.form.get('channel_id'))
    return make_response("", 200)
