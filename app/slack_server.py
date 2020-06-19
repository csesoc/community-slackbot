from flask import Flask, Blueprint, make_response, request
from slackeventsapi import SlackEventAdapter
from config import Config
import app.slack_handler as handler
import app.slack_utils as utils
import threading
import json

# Set up SlackEventAdapter and app
app = Flask(__name__, instance_relative_config=False)
slack_events_adapter = SlackEventAdapter(Config.SLACK_SIGNING_SECRET, "/slack/events", server=app)

slack = Blueprint(
    'slack', __name__,
)

# Routes
@slack.route("/", methods=['POST'])
def interactivity():
    """
    The main route for enabling interactions with shortcuts, modals, or interactive 
    components (such as buttons, select menus, and datepickers). To add an interaction,
    simply modify the code in the function app.slack_handler.interactions
    """

    # Verify request
    if not utils.verify_request(request):
        return make_response("", 400)

    # Parse request
    payload = json.loads(request.form.to_dict()["payload"])

    # Spawn a thread to service the request
    threading.Thread(target=handler.interactions, args=[payload]).start()
    return make_response("", 200)


@slack.route('/pair', methods=['POST'])
def pair():
    if not utils.verify_request(request):
        return make_response("", 400)
    return make_response("Pair success", 200)


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