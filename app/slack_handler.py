from slack import WebClient
from config import Config
import app.slack_utils as utils
import app.block_views as blocks

# Set up the slack client
client = WebClient(Config.SLACK_TOKEN)


def interactions(payload):
    """
    The main function for enabling interactions with shortcuts, modals, or 
    interactive components (such as buttons, select menus, and datepickers).
    See https://api.slack.com/reference/interaction-payloads for more details
    on how to handle interaction payloads.
    """

    # Extract data
    trigger_id = payload["trigger_id"]
    user = payload["user"]["id"]


    # Received when a user clicks a Block Kit interactive component.
    if payload["type"] == "block_actions":
        actions = payload["actions"]
        value = actions[0]["value"]

        # No modal is expected
        if value == "pass":
            pass

        # Opens the "commands_help" view
        if value == "commands_help":
            client.views_open(trigger_id=trigger_id, view=blocks.commands_help())

        # Opens the "edit_profile" view with prefilled information
        if value == "edit_profile":
            values = utils.retrieve_profile_details(user)
            client.views_open(trigger_id=trigger_id, view=blocks.edit_profile(values))


    # Received when a modal is submitted.
    if payload["type"] == "view_submission":
        view = payload["view"]
        callback_id = view["callback_id"]

        # Store submitted profile data
        if callback_id == "edit_profile_modal":
            values = view["state"]["values"]
            for key in ["favourite_course", "favourite_programming_language", "favourite_netflix_show", "favourite_food", \
                    "overrated", "underrated", "biggest_flex", "enrolled_courses", "completed_courses", "general_interests"]:
                value = utils.extract_value(values, key, key)
                utils.add_profile_details(user, key, value)


def onboarding(user, channel=None):
    """
    Onboards a new user or a existing user that hasn't been onboarded yet.
    """

    # Check if user is in the database
    if utils.query_user_exists(user):
        return

    # Add user to the database
    utils.add_new_user(user)

    # Retrieve channel
    if channel is None:
        channel = client.conversations_open(users=[user])["channel"]["id"]

    # Post the message in the channel
    client.chat_postMessage(channel=channel, text='IMPORTANT: CSESoc Slack Onboarding!!', blocks=blocks.onboarding(user))
