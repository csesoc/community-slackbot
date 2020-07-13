from slack import WebClient
import os

from buildBlocks import imBlock, mentionBlock, helpModal, globalTriviaModal, triviaCustomQuestions, triviaInviteMessage, triviaAskQuestion, triviaComplete, triviaBoard, triviaOngoing, triviaCustomMessage

slack_token = os.getenv("SLACK_TOKEN")
client = WebClient(slack_token)

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