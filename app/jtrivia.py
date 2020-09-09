import json
import random
import time
from app import client
from app.buildBlocks import imBlock, mentionBlock, helpModal, globalTriviaModal, triviaCustomQuestions, triviaInviteMessage, triviaAskQuestion, triviaComplete, triviaBoard, triviaOngoing, triviaCustomMessage

class Trivia_Game:
    def __init__(self, creator_id):
        self.creator_id = creator_id
        self.channel = None
        self.default_qs = None
        self.number_qs = None
        self.trivia_players = None
        self.questions = []
        self.view = None
        self.finished = []
    
    def __str__(self):
        return f"Creator: {self.creator_id}\nChannel: {self.channel}\nDefault Qs?: {self.default_qs}\nNumber of Qs: {self.number_qs}\nPlayers: {self.trivia_players}"

class Trivia_Player:
    def __init__(self, user_id, game_id):
        self.user_id = user_id
        self.game_id = game_id
        self.score = 0
        self.question = 1
        self.view = None
        self.time = None

trivia_games = {}
trivia_players = {}

def init_trivia(trigger_id, user_id):
    if user_id in trivia_games.keys():
        trivia_ongoing(trigger_id)
        return
    trivia_games[user_id] = Trivia_Game(user_id)
    trivia_games[user_id].view = trivia_modal(trigger_id, user_id)

def trivia_set_channel(user_id, channel_id):
    trivia_games[user_id].channel = channel_id

def trivia_set_qs(user_id, default_trivia):
    trivia_games[user_id].default_qs = default_trivia

def trivia_q_number(user_id, number_qs):
    trivia_games[user_id].number_qs = number_qs

def trivia_player_list(user_id, user_list):
    trivia_games[user_id].trivia_players = user_list

def trivia_finalise(user_id, trigger_id):
    if trivia_games[user_id].default_qs:
        with open("blocks/questionBank.json", "r") as f:
            questionBank = json.load(f)
        for _ in range(trivia_games[user_id].number_qs):
            trivia_games[user_id].questions.append(questionBank.pop(random.randint(0,len(questionBank) - 1)))
        start_trivia(user_id)
    elif len(trivia_games[user_id].questions) != 0:
        start_trivia(user_id)
    else:
        # trivia_custom_questions_prompt(user_id, trivia_games[user_id].channel)
        return True

def trivia_customs(user_id, trigger_id):
    # trivia_custom_questions_modal(trivia_games[user_id].view, trigger_id, user_id, trivia_games[user_id].number_qs)
    return triviaCustomQuestions(user_id, trivia_games[user_id].number_qs)

def trivia_custom_questions(game_id, data):
    for i in range(trivia_games[game_id].number_qs):
        trivia_games[game_id].questions.append(
            {
                'question': data[f'question_{i+1}']['number_questions']['value'],
                'answer': data[f'answer_{i+1}']['number_questions']['value'],
                'options': [data[f'wrong{j}_{i+1}']['number_questions']['value'] for j in range(1,4)]
            }
        )
    # start_trivia(game_id)

def trivia_failure(user_id, trigger_id):
    pass

def start_trivia(user_id):
    for user in trivia_games[user_id].trivia_players:
        start_trivia_message(user, trivia_games[user_id].channel, user_id)

def trivia_reply(user_id, response, game_id, trigger_id):
    trivia_response_notify(trivia_games[game_id].creator_id, trivia_games[game_id].channel, user_id, response)
    if user_id not in trivia_games[game_id].trivia_players:
        # not in game / already rejected invite
        pass
    if user_id in trivia_players.keys():
        # already in a game
        pass
    if response:
        trivia_players[user_id] = Trivia_Player(user_id, game_id)
        trivia_question(user_id, trigger_id)
    else:
        trivia_games[game_id].trivia_players.remove(user_id)
        if len(trivia_games[game_id].trivia_players) == 0:
            del trivia_games[game_id]

def trivia_question(user_id, trigger_id):
    game_id = trivia_players[user_id].game_id
    trivia_players[user_id].time = time.time()
    trivia_players[user_id].view = trivia_question_send(trigger_id, user_id, trivia_games[game_id].channel, trivia_games[game_id].questions[trivia_players[user_id].question - 1], trivia_players[user_id].question, trivia_players[user_id].view)

def trivia_response(user_id, correct, trigger_id):
    if correct:
        trivia_players[user_id].score += 50
        newTime = time.time() - trivia_players[user_id].time
        timeScore = int((60 - newTime) / 1.2)
        if timeScore > 0:
            trivia_players[user_id].score += timeScore
    if trivia_players[user_id].question == trivia_games[trivia_players[user_id].game_id].number_qs:
        trivia_complete(trivia_players[user_id].view, trivia_players[user_id].score)
        trivia_games[trivia_players[user_id].game_id].finished.append({'player': user_id, 'score': trivia_players[user_id].score})
        trivia_games[trivia_players[user_id].game_id].trivia_players.remove(user_id)
        game_id = trivia_players[user_id].game_id
        del trivia_players[user_id]
        if len(trivia_games[game_id].trivia_players) == 0:
            trivia_leaderboard(trivia_games[game_id].channel, trivia_games[game_id].finished)
            del trivia_games[game_id]
    else:
        trivia_players[user_id].question += 1
        trivia_question(user_id, trigger_id)


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
