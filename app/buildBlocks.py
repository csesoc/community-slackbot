import copy
import json
import random
from app.utils import get_courses

def mentionBlock(user_name, channel_name, **kwargs):
    with open("app/block_views/channelMention.json", "r") as f:
        blocks = json.load(f)['blocks']
        if kwargs['is_channel'] == True:
            blocks[0]['text']['text'] = blocks[0]['text']['text'].replace("$USER", user_name).replace("$CHANNEL", channel_name)
        else:
            blocks[0]['text']['text'] = blocks[0]['text']['text'].replace("$USER", user_name).replace("$CHANNEL", "this group")
        return blocks

def imBlock(user_name):
    with open("app/block_views/imGreeting.json", "r") as f:
        blocks = json.load(f)['blocks']
        blocks[0]['text']['text'] = blocks[0]['text']['text'].replace("$USER", user_name)
        return blocks

def helpModal(user_name):
    with open("app/block_views/helpCommand.json", "r") as f:
        view = json.load(f)
        view['blocks'][0]['text']['text'] = view['blocks'][0]['text']['text'].replace("$USER", user_name)
        return view

def globalTriviaModal(user_name, user_id):
    with open("app/block_views/triviaGlobal.json", "r") as f:
        filedata = f.read()
        filedata = filedata.replace("$USERID", user_id).replace("$USER", user_name)
        view = json.loads(filedata)
        return view

def triviaCustomQuestions(user_id, q_number):
    with open("app/block_views/triviaCustoms.json", "r") as f:
        view = json.load(f)
        view['callback_id'] = view['callback_id'].replace("$USERID", user_id)
        question_blocks = view['blocks']
        new_blocks = []
        for i in range(q_number):
            new_blocks += json.loads(json.dumps(question_blocks).replace("$QNUMBER", str(i + 1)))
        view['blocks'] = new_blocks
        return view

def triviaInviteMessage(game_id):
    with open("app/block_views/triviaInvite.json", "r") as f:
        blocks = json.load(f)['blocks']
        blocks[2]['elements'][0]['action_id'] = blocks[2]['elements'][0]['action_id'].replace('$GAMEID', game_id)
        blocks[2]['elements'][1]['action_id'] = blocks[2]['elements'][1]['action_id'].replace('$GAMEID', game_id)
        return blocks

def triviaAskQuestion(user, question, qnum):
    with open("app/block_views/triviaQuestion.json", "r") as f:
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
    with open("app/block_views/triviaComplete.json", "r") as f:
        filedata = f.read()
        filedata = filedata.replace("$SCORE", str(score))
        view = json.loads(filedata)
        return view

def triviaBoard(players):
    with open("app/block_views/triviaLeaderboard.json", "r") as f:
        view = json.load(f)
        playerBlock = view['blocks'].pop()
        players = sorted(players, key=lambda x: x['score'], reverse=True)
        for player in players:
            tempBlock = copy.deepcopy(playerBlock)
            tempBlock['text']['text'] = playerBlock['text']['text'].replace("$PLAYER", player['name']).replace("$SCORE", str(player['score']))
            view['blocks'].append(tempBlock)
        return view['blocks']

def triviaOngoing():
    with open("app/block_views/triviaOngoing.json", "r") as f:
        return json.load(f)

def triviaCustomMessage(user_id):
    with open("app/block_views/triviaCustomPrompt.json", "r") as f:
        filedata = f.read()
        filedata = filedata.replace("$USER", user_id)
        view = json.loads(filedata)
        return view['blocks']

def reviewModal(course_code, user_id):
    with open("app/block_views/reviewModal.json", "r") as f:
        filedata = f.read()
        filedata = filedata.replace("$USERID", user_id).replace("$COURSE", course_code)
        view = json.loads(filedata)
        return view

def reviewModalCourse(user_id):
    courses = get_courses()
    with open("app/block_views/reviewCourseModal.json", "r") as f:
        filedata = f.read()
        filedata = filedata.replace("$USERID", user_id)
        view = json.loads(filedata)
        courseBlock = view['blocks'][1]['accessory']['options'].pop()
        for course in courses:
            tempBlock = copy.deepcopy(courseBlock)
            tempBlock['text']['text'] = courseBlock['text']['text'].replace("$COURSECODE", course.course)
            tempBlock['value'] = courseBlock['value'].replace("$COURSECODE", course.course)
            view['blocks'][1]['accessory']['options'].append(tempBlock)
        return view
    

def reviewConfirm(course_code):
    with open("app/block_views/reviewConfirm.json", "r") as f:
        filedata = f.read()
        filedata = filedata.replace("$COURSE", course_code)
        view = json.loads(filedata)
        return view['blocks']

def karmaBoard(info):
    with open("app/block_views/karmaBoard.json", "r") as f:
        view = json.load(f)
        userBlock = view['blocks'].pop()
        for user in info:
            tempBlock = copy.deepcopy(userBlock)
            tempBlock['text']['text'] = userBlock['text']['text'].replace("$USER", user['name']).replace("$KARMA", str(user['karma']))
            tempBlock['accessory']['image_url'] = userBlock['accessory']['image_url'].replace("$PIC72", user['pfp'])
            tempBlock['accessory']['alt_text'] = userBlock['accessory']['alt_text'].replace("$USER", user['name'])
            view['blocks'].append(tempBlock)
        return view['blocks']

def escapeRoom(user_id, escape_num):
    with open(f"app/block_views/escape{escape_num}.json", "r") as f:
        filedata = f.read()
        filedata = filedata.replace("$USER", user_id)
        view = json.loads(filedata)
        return view