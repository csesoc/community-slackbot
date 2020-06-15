from slack import WebClient
from flask import make_response
import zutil
import block_views as blocks
import os
import json

# Set up slack client
client = WebClient(os.environ['SLACK_TOKEN'])

def interactions(request):

    # Verify request
    if not zutil.verify_request(request):
        return

    payload = json.loads(request.form.to_dict()["payload"])
    trigger_id = payload["trigger_id"]
    user = payload["user"]["id"]

    if payload["type"] == "block_actions":
        actions = payload["actions"]
        value = actions[0]["value"]

        # No modal is expected
        if value == "pass":
            pass

        # Opens the "commands_help" view
        if value == "commands_help":
            client.views_open(trigger_id=trigger_id, view=blocks.commands_help())

        # Opens the "edit_profile" view
        if value == "edit_profile":
            client.views_open(trigger_id=trigger_id, view=blocks.edit_profile())

    if payload["type"] == "view_submission":
        view = payload["view"]
        callback_id = view["callback_id"]

        # Store submitted profile data
        if callback_id == "edit_profile_modal":
            values = view["state"]["values"]
            for key in ["favourite_course", "favourite_programming_language", "favourite_netflix_show", "favourite_food", \
                    "overrated", "underrated", "biggest_flex", "enrolled_courses", "completed_courses", "general_interests"]:
                value = zutil.extract_value(values, key, key)
                zutil.add_profile_attributes(user, key, value)


def onboarding(user, channel=None):

    # Check if user is in the database
    if zutil.query_user_exists(user):
        return

    # Add user to the database
    zutil.add_new_user(user)

    # Retrieve channel
    if channel is None:
        channel = client.conversations_open(users=[user])["channel"]["id"]

    # Post the message in the channel
    client.chat_postMessage(channel=channel, text='IMPORTANT: CSESoc Slack Onboarding!!', blocks=blocks.onboarding(user))
