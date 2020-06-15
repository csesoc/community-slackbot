from slackeventsapi import SlackEventAdapter
from flask import Flask, request, make_response
import os
import zhandler

# Set up flask and slack events adapter
app = Flask(__name__)
slack_signing_secret = os.environ['SLACK_SIGNING_SECRET']
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events", server=app)

# Routes
@app.route("/", methods=['POST'])
def interactivity():
    # Spawn a thread to service the request
    zhandler.interactions(request)
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
    zhandler.onboarding(user)


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
    zhandler.onboarding(user, channel)


# Main function
if __name__ == '__main__':
    app.run(port=3000)