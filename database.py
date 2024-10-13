import json
from tinydb import TinyDB, Query

class Database:
    def __init__(self):
        self.db = TinyDB('data/game_data.json')

    def save_game_state(self, game_state: dict):
        self.db.truncate()
        self.db.insert(game_state)

    def load_game_state(self) -> dict:
        data = self.db.all()
        return data[0] if data else None

def initialize_database():
    return Database()
