import app.slack_utils as utils
from app import client
from app.block_views import get_anonymous_modal

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
    if payload["type"] == "shortcut":

        callback_id = payload["callback_id"]

        # Opens the "edit_profile" view with prefilled information
        if callback_id == "anonymous_messaging":
            client.views_open(trigger_id=trigger_id, view=get_anonymous_modal())


    # Received when a modal is submitted.
    if payload["type"] == "view_submission":
        view = payload["view"]
        callback_id = view["callback_id"]
        state = view["state"]

        # Store submitted profile data
        if callback_id == "anonymous_messaging_modal":
            print(view["state"])
            if len(view["state"]) >= 2:
                pass
