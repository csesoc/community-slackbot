import json

def mentionBlock(user_name, channel_name, **kwargs):
    with open("blocks/channelMention.json", "r") as f:
        blocks = json.load(f)['blocks']
        if kwargs['is_channel'] == True:
            blocks[0]['text']['text'] = blocks[0]['text']['text'].replace("$USER", user_name).replace("$CHANNEL", channel_name)
        else:
            blocks[0]['text']['text'] = blocks[0]['text']['text'].replace("$USER", user_name).replace("$CHANNEL", "this group")
        return blocks

def imBlock(user_name):
    with open("blocks/imGreeting.json", "r") as f:
        blocks = json.load(f)['blocks']
        blocks[0]['text']['text'] = blocks[0]['text']['text'].replace("$USER", user_name)
        return blocks
