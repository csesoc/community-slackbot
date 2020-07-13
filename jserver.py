from slackeventsapi import SlackEventAdapter
from flask import Flask, request, make_response, Response
import requests
import hmac
import os
import hashlib
import json
import random

from jhandler import reply_mention, reply_im, help_modal, trivia_modal
from jother import verify_request
from jtrivia import init_trivia, trivia_set_channel, trivia_set_qs, trivia_q_number, trivia_player_list, trivia_finalise, trivia_failure, start_trivia, trivia_reply, trivia_response, trivia_customs, trivia_custom_questions

app = Flask(__name__)
slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/", server=app)

@app.route('/', methods=['POST'])
def slack_root():
    attributes = request.get_json()
    if 'challenge' in attributes:
        return Response(attributes['challenge'], mimetype="text/plain")
    return Response()

@app.route('/shortcut', methods=['POST'])
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
                trivia_finalise(game_id, attributes['trigger_id'])
            except:
                trivia_failure(game_id, attributes['trigger_id'])
        elif 'custom_questions_' in attributes['view']['callback_id']:
            trivia_custom_questions(attributes['view']['callback_id'].replace('custom_questions_', ''), attributes['view']['state']['values'])

    return Response()

@slack_events_adapter.on("app_mention")
def slack_mention(event_data):
    user = event_data['event']['user']
    channel = event_data["event"]["channel"]
    reply_mention(user, channel)

@slack_events_adapter.on("message")
def slack_im(event_data):
    # message was edited/deleted
    if "user" not in event_data["event"]:
        return
    user = event_data["event"]["user"]
    channel = event_data["event"]["channel"]
    # wont respond to bots
    if 'bot_id' not in event_data['event'] and 'text' in event_data['event']:
        message = event_data['event']['text']
        reply_im(user, channel, message)

@app.route('/helpme', methods=['POST'])
def slack_help():
    if not verify_request(request):
        return make_response("",400)
    help_modal(request.form.get('trigger_id'), request.form.get('user_id'))
    return make_response("", 200)

if __name__ == '__main__':
    app.run(port=3000, debug=True, threaded=True)
