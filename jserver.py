from slackeventsapi import SlackEventAdapter
from flask import Flask, request, make_response, Response
import requests
import hmac
import os
import hashlib
import json
import random

from jhandler import reply_mention, reply_im

app = Flask(__name__)
slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/", server=app)

@app.route('/', methods=['POST'])
def slack_root():
    attributes = request.get_json()
    if 'challenge' in attributes:
        return Response(attributes['challenge'], mimetype="text/plain")
    return Response()

@slack_events_adapter.on("app_mention")
def slack_mention(event_data):
    user = event_data['event']['user']
    channel = event_data["event"]["channel"]
    reply_mention(user, channel)

@slack_events_adapter.on("message")
def slack_im(event_data):
    user = event_data["event"]["user"]
    channel = event_data["event"]["channel"]
    if 'bot_id' not in event_data['event'] and 'text' in event_data['event']:
        message = event_data['event']['text']
        reply_im(user, channel, message)

if __name__ == '__main__':
    app.run(port=3000, debug=True, threaded=True)
