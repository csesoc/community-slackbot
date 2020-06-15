from slack import WebClient
import os

from buildBlocks import imBlock, mentionBlock

slack_token = os.getenv("SLACK_TOKEN")
client = WebClient(slack_token)

greetings = ["Hi"]

def reply_mention(user, channel):
    user_info = client.users_info(user=user)['user']
    user_name = user_info['profile']['display_name_normalized'] if (user_info['profile']['display_name_normalized'] != "") else user_info['profile']['real_name_normalized']
    channel_info = client.conversations_info(channel=channel)['channel']
    channel_name = channel_info['name']
    message = f"Hi {user_name}, it's me slackbot!"
    client.chat_postMessage(channel=channel, text=message, blocks=mentionBlock(user_name, channel_name, is_channel=channel_info['is_channel']))

def reply_im(user, channel, message):
    if message not in greetings:
        return
    user_info = client.users_info(user=user)['user']
    user_name = user_info['profile']['display_name_normalized'] if (user_info['profile']['display_name_normalized'] != "") else user_info['profile']['real_name_normalized']
    message = f"Hi {user_name}, it's me slackbot!"
    client.chat_postMessage(channel=channel, text=message, blocks=imBlock(user_name))
