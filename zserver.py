from slackeventsapi import SlackEventAdapter
from slack import WebClient
from flask import Flask, request, make_response
import block_views as blocks
import os
import json
import settings

# Set up flask
app = Flask(__name__)
slack_signing_secret = os.environ['SLACK_SIGNING_SECRET']
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events", server=app)

slack_token = os.environ['SLACK_TOKEN']
client = WebClient(slack_token)

# Set up db
users = []

# Routes
@app.route("/", methods=['POST'])
def interactivity():
    payload = json.loads(request.form.to_dict()["payload"])
    trigger_id = payload["trigger_id"]
    user = payload["user"]["id"]

    if payload["type"] == "block_actions":
        actions = payload["actions"]
        value = actions[0]["value"]

        # No modal is expected
        if value == "pass":
            return make_response("", 200)

        # Returns the "commands_help" view
        if value == "commands_help":
            client.views_open(trigger_id=trigger_id, view=blocks.commands_help())
            return make_response("", 200)

        # Returns the "edit_profile" view
        if value == "edit_profile":
            client.views_open(trigger_id=trigger_id, view=blocks.edit_profile())
            return make_response("", 200)

    if payload["type"] == "view_submission":
        view = payload["view"]
        callback_id = view["callback_id"]

        # Response to submission of profile data
        if callback_id == "edit_profile_modal":
            values = view["state"]["values"]
            extract_value = lambda key : values[key][key]["value"] if "value" in values[key][key].keys() else None

            # Extract data from form submission
            most_overrated_thing = extract_value("overrated")
            most_underrated_thing = extract_value("underrated")
            biggest_flex = extract_value("biggest_flex")
            enrolled_courses = extract_value("enrolled_courses")
            completed_courses = extract_value("completed_courses")
            general_interests = extract_value("general_interests")

            # Save information to database
            print(most_overrated_thing)
            print(most_underrated_thing)
            print(biggest_flex)
            print(enrolled_courses)
            print(completed_courses)
            print(general_interests)

            return make_response("", 200)

# Events
@slack_events_adapter.on("team_join")
def team_join(payload):
    '''
    Onboarding will trigger on both the "team_join" and "app_home_opened" event.
    This is to ensure that new, returning, and existing users of the slack space 
    can easily be onboarded and added to the database without any problems. 
    "team_join" will require an extra step, which is finding the channel.
    '''
    # Retrieve event data
    event = payload["event"]

    # Check if user is in the database
    user = event["user"]
    if user in users:
        return

    # Add user to the database
    users.append(user)

    # Get channel
    channel = client.conversations_open(users=[user])["channel"]["id"]

    # Post the message in the channel
    client.chat_postMessage(channel=channel, text='csesoc slack onboarding', blocks=blocks.onboarding(user))


@slack_events_adapter.on("app_home_opened")
def app_home_opened(payload):

    # Retrieve event data
    event = payload["event"]

    # Check if user is in the database
    user = event["user"]
    if user in users:
        return

    # Add user to the database
    users.append(user)

    # Post the message in the channel
    client.chat_postMessage(channel=event["channel"], text='csesoc slack onboarding', blocks=blocks.onboarding(user))


# Main function
if __name__ == '__main__':
    app.run(port=3000)