import json

def onboarding(user_id):
    with open("blocks/onboarding.json", "r") as fp:
        blocks = json.load(fp)["blocks"]
        blocks[0]["text"]["text"] = blocks[0]["text"]["text"].replace("%%USER%%", f"<@{user_id}>")
        return blocks

def edit_profile():
    with open("blocks/edit_profile.json", "r") as fp:
        return json.load(fp)

def commands_help():
    with open("blocks/commands_help.json", "r") as fp:
        return json.load(fp)