from flask import json

import app.slack_utils as utils
from app import client
from app.block_views import get_anonymous_modal, get_anonymous_message, get_anonymous_reply_modal, get_report_modal


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
            controls = []
            # Unwrap control
            for control in list(state["values"].items()):
                control = control[1]
                control = list(control.items())[0][1]
                print(control)
                controls.append(control)

            users = controls[0]["selected_users"]
            message = controls[1]["value"]
            msg_ids = utils.create_anon_message(user, users, message)
            for i, selected_user in enumerate(users):
                block = get_anonymous_message(message, msg_ids[i])
                client.chat_postMessage(channel=selected_user, blocks=block)
        elif callback_id.startswith("anonymous_messaging_modal_reply"):
            view = payload["view"]
            state = view["state"]
            message_id = callback_id.split("=")[1]
            # Unwrap control
            control = list(state["values"].items())
            control = control[0][1]
            control = list(control.items())[0][1]
            reply_msg = control["value"]
            print(reply_msg)
            reply = utils.reply_anon_message(user, message_id, reply_msg)
            block = get_anonymous_message(reply_msg, reply.id)
            client.chat_postMessage(channel=reply.target_id, blocks=block)
        elif callback_id.startswith("report_messaging_modal_reply"):
            view = payload["view"]
            state = view["state"]
            message_id = callback_id.split("=")[1]
            # Unwrap control
            control = list(state["values"].items())
            control = control[0][1]
            control = list(control.items())[0][1]
            report_msg = control["value"]
            print(report_msg)
            report_id = utils.report_message(message_id, report_msg)
            client.chat_postMessage(channel=payload["user"]["id"],
                                    text="Message Reported, to follow up "
                                         "provide the following report id: R{}".format(report_id))

    if payload["type"] == "block_actions":
        action = payload["actions"][0]["value"]
        message_id = payload["message"]["blocks"][0]["block_id"]
        print(message_id)
        if action == "click_report":
            client.views_open(trigger_id=trigger_id, view=get_report_modal(message_id))
        elif action == "click_reply":
            client.views_open(trigger_id=trigger_id, view=get_anonymous_reply_modal(message_id))