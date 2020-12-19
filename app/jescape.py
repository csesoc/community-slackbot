from app import client
from app.buildBlocks import escapeRoom

class Escape_Game:
    def __init__(self, id, view):
        self.id = id
        self.view = view

escape_games = {}

def init_escape(id, view):
    escape_games[id] = Escape_Game(id, view)

def get_view(id):
    return escape_games[id].view

def remove_escape(id):
    del escape_games[id]

def update_escape(id, escape_count):
    return client.views_update(view_id=get_view(id), view=escapeRoom(id, escape_count))
    
def escape_modal(id, escape_count):
    return escapeRoom(id, escape_count)
