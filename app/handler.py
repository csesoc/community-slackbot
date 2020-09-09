#function handlers to service user requests 
import app.utils as utils
from app import client, user_client
import os
from flask import json
from app.block_views import get_anonymous_modal, get_anonymous_message, get_anonymous_reply_modal, get_report_modal
import app.block_views as blocks
from app.buildBlocks import imBlock, mentionBlock, helpModal, globalTriviaModal, triviaCustomQuestions, triviaInviteMessage, triviaAskQuestion, triviaComplete, triviaBoard, triviaOngoing, triviaCustomMessage, reviewModal, karmaBoard, reviewConfirm

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
        if callback_id == "edit_profile_modal":
            values = view["state"]["values"]
            for key in ["favourite_course", "favourite_programming_language", "favourite_netflix_show", "favourite_food", \
                    "overrated", "underrated", "biggest_flex", "enrolled_courses", "completed_courses", "general_interests"]:
                value = utils.extract_value(values, key, key)
                utils.add_profile_details(user, key, value)
            app_home({"user": user})

        # Purge messages
        if callback_id == "purge_confirmation":
            # Extract metadata
            metadata = blocks.json.loads(view["private_metadata"])

            # Signal the purge is starting
            client.chat_postEphemeral(channel=metadata["channel_id"], user=user, text="Purging messages...")

            # Retrieve data from metadata
            number_of_messages = metadata["number_of_messages"]
            target_user_id = metadata["user"][2:13]
            oldest = int(utils.time.time()) - metadata["time_period"] if metadata["time_period"] != -1 else 0   
            channel_id = metadata["channel_id"]
            text_snippet = metadata["text_snippet"]

            # Get messages from channel
            conversations_history = client.conversations_history(channel=channel_id, oldest=oldest).data

            # Iterate through messages and delete messages until we run out of messages to delete or reach our target
            count_deleted = 0
            while count_deleted < number_of_messages:

                # Iterate through messages
                for msg in conversations_history["messages"]:

                    # Skip messages that are not actual messages (e.g event messages)
                    if msg["type"] != "message":
                        continue

                    # Delete if no user specified or user of message matches target
                    if (target_user_id == "" or target_user_id == msg["user"]) and (text_snippet == "" or text_snippet in blocks.json.dumps(msg)):
                        try:
                            user_client.chat_delete(channel=channel_id, ts=msg["ts"])
                            count_deleted += 1
                        except Exception as e:
                            # Serve error back to user for debugging
                            client.chat_postEphemeral(channel=metadata["channel_id"], user=user, text=str(e))
                            quit()

                    # Break loop if target number of messages is reached
                    if count_deleted >= number_of_messages:
                        break

                # Check that there are more messages to retrieve
                if conversations_history["has_more"] is False:
                    break

                # Retrieve next set of messages
                cursor = conversations_history["response_metadata"]["next_cursor"]
                conversations_history = client.conversations_history(channel=channel_id, oldest=oldest, cursor=cursor)

            # Signal the purge is complete
            client.chat_postEphemeral(channel=metadata["channel_id"], user=user, text="Purge complete")

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

        # Received when a user clicks a Block Kit interactive component.
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


def cs_job_opportunities(payload):
    """
    Lets you know about CS job opportunities from indeed
    Usage: /CSopportunities [OPTIONS, page_number=1, query="software internship"]
    """

    # Extract the text from the payload
    text = payload["text"].strip()

    # Attempt to extract options
    options=""
    if "-r" in text:
        text = text.replace("-r", "")
        options += "&sort=date"

    # Attempt to extract the page number from the given text
    try:
        page_number = text.split()[0]
        page_number = int(page_number)
    except:
        page_number = 1

    # Attempt to extract the query from the given text
    query = text.lstrip('0123456789.- ') 
    if query == "":
        query = "software internship"

    # Retrieve jobs
    message, jobs = utils.jobs_from_indeed(page_number, query, options)

    # Open modal with jobs
    client.views_open(trigger_id=payload["trigger_id"], view=blocks.job_opportunities(query, message, jobs))


def purge(payload):
    """
    Mass delete unwanted messages.
    Usage: /purge <number of messages> [user, time_period, text_snippet]
    """

    # Retrieve permission level of user_id
    perm_level, _ = utils.retrieve_highest_permission_level(payload["user_id"])

    # Deny request if user doesn't have enough permission
    if perm_level <= 0:
        client.views_open(trigger_id=payload["trigger_id"], view=blocks.permission_denied())
        return

    # Extract number of messages
    text = payload["text"].strip()
    try:
        number_of_messages = int(text.split()[0])
        text = text.replace(str(number_of_messages), "", 1).strip()
        if number_of_messages <= 0:
            raise ValueError
    except:
        client.views_open(trigger_id=payload["trigger_id"], view=blocks.error_message("Invalid number of messages"))
        return

    # Extract user from arguments
    user = ""
    if text != "" and utils.re.search("^<@[A-Z0-9]+|.*>$", text.split()[0]):
        user = text.split()[0]
        text = text.replace(user, "").strip()

    # Extract time period from arguments
    time_period = -1
    if text != "" and utils.re.search("^[0-9]+$", text.split()[0]):
        time_period = int(text.split()[0])
        text = text.replace(str(time_period), "", 1).strip()

    # Extract text snippet from arguments
    text_snippet = text

    # Open purge confirmation modal
    client.views_open(trigger_id=payload["trigger_id"], view=blocks.purge_confirmation(number_of_messages, user, time_period, payload["channel_id"], text_snippet))


def say(payload):
    """
    Say something as the SlackBot
    """
    print('Got here')
    client.chat_postMessage(channel=payload["channel_id"], text=payload["text"])


def app_home(event):
    """
    Publish app home to the user
    """

    # Retrieve user profile details from slack
    user = event["user"]
    user_profile = client.users_profile_get(user=user)

    # Retrieve profile details from database 
    values = utils.retrieve_profile_details(user)
    _, title = utils.retrieve_highest_permission_level(user)

    data = {
        "image_original": user_profile["profile"]["image_original"],
        "full_name": user_profile["profile"]["real_name"],
        "username": user_profile["profile"]["real_name"].lower().replace(" ", "_"),
        "values": values,
        "role": title,
        "join_date": utils.retrieve_created_at(user)
    }
    client.views_publish(user_id=user, view=blocks.app_home(data))


greetings = ["hi", "hello"]

def reply_mention(user, channel):
    user_info = client.users_info(user=user)['user']
    user_name = user_info['profile']['display_name_normalized'] if (user_info['profile']['display_name_normalized'] != "") else user_info['profile']['real_name_normalized']
    channel_info = client.conversations_info(channel=channel)['channel']
    channel_name = channel_info['name']
    message = f"Hi {user_name}, it's me slackbot!"
    client.chat_postMessage(channel=channel, text=message, blocks=mentionBlock(user_name, channel_name, is_channel=channel_info['is_channel']))

def reply_im(user, channel, message):
    if message.lower() not in greetings:
        return
    user_info = client.users_info(user=user)['user']
    user_name = user_info['profile']['display_name_normalized'] if (user_info['profile']['display_name_normalized'] != "") else user_info['profile']['real_name_normalized']
    message = f"Hi {user_name}, it's me slackbot!"
    client.chat_postMessage(channel=channel, text=message, blocks=imBlock(user_name))

def help_modal(trigger_id, user):
    user_info = client.users_info(user=user)['user']
    user_name = user_info['profile']['display_name_normalized'] if (user_info['profile']['display_name_normalized'] != "") else user_info['profile']['real_name_normalized']
    client.views_open(trigger_id=trigger_id, view=helpModal(user_name))

def trivia_modal(trigger_id, user):
    user_info = client.users_info(user=user)['user']
    user_name = user_info['profile']['display_name_normalized'] if (user_info['profile']['display_name_normalized'] != "") else user_info['profile']['real_name_normalized']
    return client.views_open(trigger_id=trigger_id, view=globalTriviaModal(user_name, user))['view']['id']

def trivia_custom_questions_modal(view_id, trigger_id, user, q_number):
    # client.views_update(view_id=view_id, view=triviaCustomQuestions(user, q_number))
    # client.views_push(trigger_id=trigger_id, view=triviaCustomQuestions(user, q_number))
    client.views_open(trigger_id=trigger_id, view=triviaCustomQuestions(user, q_number))

def start_trivia_message(user, channel, game_id):
    client.chat_postEphemeral(user=user, channel=channel, text="Trivia Time", blocks=triviaInviteMessage(game_id))

def trivia_response_notify(user, channel, player, response):
    player_info = client.users_info(user=player)['user']
    player_name = player_info['profile']['display_name_normalized'] if (player_info['profile']['display_name_normalized'] != "") else player_info['profile']['real_name_normalized']
    if response:
        client.chat_postEphemeral(user=user, channel=channel, text=f"{player_name} accepted your trivia invite")
    else:
        client.chat_postEphemeral(user=user, channel=channel, text=f"{player_name} rejected your trivia invite")

def trivia_question_send(trigger_id, user, channel, question, qnum, view):
    if view is None:
        return client.views_open(trigger_id=trigger_id, view=triviaAskQuestion(user, question, qnum))['view']['id']
    else:
        return client.views_update(view_id=view, view=triviaAskQuestion(user, question, qnum))['view']['id']

def trivia_complete(view, score):
    return client.views_update(view_id=view, view=triviaComplete(score))

def trivia_leaderboard(channel, players):
    for player in players:
        player_info = client.users_info(user=player['player'])['user']
        player['name'] = player_info['profile']['display_name_normalized'] if (player_info['profile']['display_name_normalized'] != "") else player_info['profile']['real_name_normalized']
    client.chat_postMessage(channel=channel, text="Trivia is over!", blocks=triviaBoard(players))

def trivia_ongoing(trigger_id):
    client.views_open(trigger_id=trigger_id, view=triviaOngoing())

def trivia_custom_questions_prompt(user_id, channel):
    client.chat_postEphemeral(user=user_id, channel=channel, text="Fill in custom questions", blocks=triviaCustomMessage(user_id))

def review_modal(trigger_id, course_code, user_id):
    return client.views_open(trigger_id=trigger_id, view=reviewModal(course_code, user_id))['view']['id']

def review_confirm(user_id, course_code):
    client.chat_postMessage(channel=user_id, blocks=reviewConfirm(course_code))

def karma_message(channel_id):
    toppers = utils.get_top_karma()
    # display name, profile picture, karma count
    leaders = []
    for user in toppers:
        player_info = client.users_info(user=user.id)['user']
        player_name = player_info['profile']['display_name_normalized'] if (player_info['profile']['display_name_normalized'] != "") else player_info['profile']['real_name_normalized']
        leaders.append({'name': player_name, 'karma': user.karma, 'pfp': player_info['profile']['image_72']})
    client.chat_postMessage(channel=channel_id, text="Karma boards", blocks=karmaBoard(leaders))