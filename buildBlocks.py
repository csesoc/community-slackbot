import json
import random

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

def helpModal(user_name):
    with open("blocks/helpCommand.json", "r") as f:
        view = json.load(f)
        view['blocks'][0]['text']['text'] = view['blocks'][0]['text']['text'].replace("$USER", user_name)
        return view

def globalTriviaModal(user_name, user_id):
    with open("blocks/triviaGlobal.json", "r") as f:
        filedata = f.read()
        filedata = filedata.replace("$USERID", user_id).replace("$USER", user_name)
        view = json.loads(filedata)
        return view

def triviaCustomQuestions(user_id, q_number):
    with open("blocks/triviaCustoms.json", "r") as f:
        view = json.load(f)
        view['callback_id'] = view['callback_id'].replace("$USERID", user_id)
        question_blocks = view['blocks']
        new_blocks = []
        for i in range(q_number):
            new_blocks += json.loads(json.dumps(question_blocks).replace("$QNUMBER", str(i + 1)))
        view['blocks'] = new_blocks
        return view

def triviaInviteMessage(game_id):
    with open("blocks/triviaInvite.json", "r") as f:
        blocks = json.load(f)['blocks']
        blocks[2]['elements'][0]['action_id'] = blocks[2]['elements'][0]['action_id'].replace('$GAMEID', game_id)
        blocks[2]['elements'][1]['action_id'] = blocks[2]['elements'][1]['action_id'].replace('$GAMEID', game_id)
        return blocks

def triviaAskQuestion(user, question, qnum):
    with open("blocks/triviaQuestion.json", "r") as f:
        filedata = f.read()
        filedata = filedata.replace("$GAMEID", user).replace("$QNUM", str(qnum)).replace("$QUESTION", question['question'])
        numList = [1,2,3,4]
        choice = numList.pop(random.randint(0, len(numList) - 1))
        filedata = filedata.replace(f"$OPTION{choice}", question['answer']).replace(f"$VALUE{choice}", "correct")
        for i in range(3):
            choice = numList.pop(random.randint(0, len(numList) - 1))
            filedata = filedata.replace(f"$OPTION{choice}", question['options'][i]).replace(f"$VALUE{choice}", "wrong")
        view = json.loads(filedata)
        return view

def triviaComplete(score):
    with open("blocks/triviaComplete.json", "r") as f:
        filedata = f.read()
        filedata = filedata.replace("$SCORE", str(score))
        view = json.loads(filedata)
        return view

def triviaBoard(players):
    with open("blocks/triviaLeaderboard.json", "r") as f:
        view = json.load(f)
        playerBlock = view['blocks'].pop()
        players = sorted(players, key=lambda x: x['score'], reverse=True)
        for player in players:
            tempBlock = playerBlock
            tempBlock['text']['text'] = playerBlock['text']['text'].replace("$PLAYER", player['name']).replace("$SCORE", str(player['score']))
            view['blocks'].append(tempBlock)
        return view['blocks']

def triviaOngoing():
    with open("blocks/triviaOngoing.json", "r") as f:
        return json.load(f)

def triviaCustomMessage(user_id):
    with open("blocks/triviaCustomPrompt.json", "r") as f:
        filedata = f.read()
        filedata = filedata.replace("$USER", user_id)
        view = json.loads(filedata)
        return view['blocks']